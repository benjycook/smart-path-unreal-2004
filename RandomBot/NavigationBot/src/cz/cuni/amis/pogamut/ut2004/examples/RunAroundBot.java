package cz.cuni.amis.pogamut.ut2004.examples;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.logging.Level;

import javax.swing.Timer;

import cz.cuni.amis.pogamut.base.agent.navigation.PathEventType;
import cz.cuni.amis.pogamut.base.agent.navigation.PathExecutorListener;
import cz.cuni.amis.pogamut.base.agent.navigation.PathPlanner;
import cz.cuni.amis.pogamut.base.utils.guice.AgentScoped;
import cz.cuni.amis.pogamut.base3d.worldview.object.ILocated;
import cz.cuni.amis.pogamut.base3d.worldview.object.Location;
import cz.cuni.amis.pogamut.ut2004.agent.navigation.UTPathExecutor;
import cz.cuni.amis.pogamut.ut2004.agent.navigation.floydwarshall.FloydWarshallPathPlanner;
import cz.cuni.amis.pogamut.ut2004.bot.impl.UT2004Bot;
import cz.cuni.amis.pogamut.ut2004.bot.impl.UT2004BotLogicController;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbcommands.Initialize;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbcommands.Respawn;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbinfomessages.BotKilled;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbinfomessages.Item;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbinfomessages.Self;
import cz.cuni.amis.pogamut.ut2004.communication.translator.itemdescriptor.WeaponDescriptor;
import cz.cuni.amis.pogamut.ut2004.factory.guice.remoteagent.UT2004BotFactory;
import cz.cuni.amis.pogamut.ut2004.factory.guice.remoteagent.UT2004BotModule;
import cz.cuni.amis.pogamut.ut2004.utils.SingleUT2004BotRunner;
import cz.cuni.amis.pogamut.ut2004.utils.UT2004BotRunner;
import cz.cuni.amis.utils.exception.PogamutException;

/**
 * Navigation testing bot which runs around all weapons in the map.
 * 
 * @author ondra
 */
@AgentScoped
public class RunAroundBot extends UT2004BotLogicController {

	/**
	 * Executor is used for following a path in the environment.
	 */
	protected UTPathExecutor pathExecutor = null;
	/**
	 * Flag indicating that the bot has been just executed.
	 */
	protected boolean first = true;
	private List<Item> weapons;
	private Iterator<Item> iterator;
	private int pathCount = 0;
	private boolean ready = true;
	private boolean executing;
	private Timer timer;
	private ActionListener listener;
	private PathPlanner<ILocated, ILocated> pathPlanner;
	private Location location;

	/**
	 * Here we have already received information about game in GameInfo
	 * 
	 * @param info
	 */
	@Override
	public void prepareBot(UT2004Bot bot) {
		super.prepareBot(bot);
		prepareWeapons();
		prepareTimer();
		bot.getLogger().setLevel(Level.WARNING);
	}

	/**
	 * Here we can modify initializing command for our bot.
	 * 
	 * @return
	 */
	@Override
	public Initialize getInitializeCommand() {
		// just set the name of the bot, nothing else
		return new Initialize().setName("RunAroundBot");
	}

	/**
	 * Main method that controls the bot - makes decisions what to do next. It
	 * is called iteratively by Pogamut engine every time a synchronous batch
	 * from the environment is received. This is usually 4 times per second -
	 * it is affected by visionTime variable, that can be adjusted in GameBots
	 * ini file in UT2004/System folder.
	 * 
	 * @throws cz.cuni.amis.pogamut.base.exceptions.PogamutException
	 */
	@Override
	public void logic() throws PogamutException {

		if (first) {
			// create the path planner, it will be used to compute paths between
			// two navpoints
			pathPlanner = new FloydWarshallPathPlanner(bot);
//			pathPlanner = new UTAstar(bot);

			// create new path executor
			pathExecutor = new UTPathExecutor(bot); // notice that the path
													// executor has pointer to
													// the path planner

			// specify what will happen when the bot reaches its destination
			pathExecutor.addPathListener(new PathExecutorListener() {

				public void onEvent(PathEventType eventType) {
					if (eventType.equals(PathEventType.TARGET_REACHED)) {
						processTargetReached();
					}
					if (eventType.equals(PathEventType.PATH_BROKEN)
							|| eventType.equals(PathEventType.FAILURE)
							|| eventType.equals(PathEventType.TARGET_UNREACHABLE)
							|| eventType.equals(PathEventType.BOT_STUCKED)) {
						processPathProblem(eventType);
					}
				}

			});

			// start the movement
			goToAnotherGoal();

			first = false;
		}
	}

	protected void processTargetReached() {
		log("----- TARGET REACHED -----");
		if (getAgentLocation().getDistance(location) < 100) {
			pathCount = 0;
			goToAnotherGoal();
			executing = true;					
		} else {
			runToTheTarget();
		}
	}

	private Location getAgentLocation() {
		return getWorldView().getSingle(Self.class).getLocation();
	}

	protected void processPathProblem(PathEventType eventType) {
		executing = false;
		if (ready) {
			log("------------------ PATH BROKEN -------------------- "
					+ eventType.name());
			pathCount++;
			if (pathCount > 10) {
				pathCount = 0;
				getAct().act(
						new Respawn().setStartLocation(getNextItem()
								.getLocation()));
			}
			ready = false;
			goToAnotherGoal();
		} else {
			log("------------------ PATH BROKEN -------------------- and restart " + eventType.name());
			timer.restart();
		}
	}

	/**
	 * Go to the next weapon in the list.
	 */
	protected void goToAnotherGoal() {
		location = getNextItem().getLocation();
		runToTheTarget();
	}

	protected void runToTheTarget() {
		pathExecutor.followPath(pathPlanner.computePath(location));
	}

	protected void prepareWeapons() {
		weapons = new ArrayList<Item>(20);
		for (Item item : getWorldView().getAll(Item.class).values()) {
			if (item.getDescriptor() instanceof WeaponDescriptor) {
				weapons.add(item);
			}
		}
		if (weapons.isEmpty()) {
			System.err.println("Weapons can't be empty!!! Unable to proceed!");
			bot.kill();
		}
		iterator = weapons.iterator();
	}

	/**
	 * Picks another weapon to run to. If there is no other - shuffle the list
	 * and go again.
	 */
	private Item getNextItem() {
		if (!iterator.hasNext()) {
			Collections.shuffle(weapons);
			iterator = weapons.iterator();
		}

		return iterator.next();
	}

	/**
	 * Called each time our bot die. Good for reseting all bot state dependent
	 * variables.
	 * 
	 * @param event
	 */
	@Override
	public void botKilled(BotKilled event) {
		timer.stop();
	}

	public static void main(String args[]) throws PogamutException {
		new SingleUT2004BotRunner<UT2004Bot>(RunAroundBot.class, "RunAroundBot").startAgent();
	}

	private void log(String string) {
//		bot.getLogger().getCategories().values().iterator().next().info(string);
		 System.err.println(string);
	}

	private void prepareTimer() {
		listener = new ActionListener() {

			public void actionPerformed(ActionEvent e) {
				ready = true;
				timer.stop();
				if (!executing) {
					goToAnotherGoal();
					log("go to another goal!");
				}
			}
		};
		timer = new Timer(3000, listener);
	}
}
