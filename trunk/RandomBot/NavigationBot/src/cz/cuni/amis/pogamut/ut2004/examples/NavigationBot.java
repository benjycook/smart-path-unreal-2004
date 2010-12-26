package cz.cuni.amis.pogamut.ut2004.examples;

import cz.cuni.amis.pogamut.ut2004.agent.module.sensor.Players;
import java.util.Collection;

import cz.cuni.amis.introspection.java.JProp;
import cz.cuni.amis.pogamut.base.agent.navigation.PathEventType;
import cz.cuni.amis.pogamut.base.agent.navigation.PathExecutorListener;
import cz.cuni.amis.pogamut.base.agent.navigation.PathHandle;
import cz.cuni.amis.pogamut.base.utils.guice.AgentScoped;
import cz.cuni.amis.pogamut.base.utils.math.DistanceUtils;
import cz.cuni.amis.pogamut.base3d.worldview.object.ILocated;
import cz.cuni.amis.pogamut.ut2004.agent.navigation.stuckdetectors.StupidStuckDetector;
import cz.cuni.amis.pogamut.ut2004.bot.impl.UT2004Bot;
import cz.cuni.amis.pogamut.ut2004.bot.impl.UT2004BotModuleController;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbcommands.Initialize;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbinfomessages.BotKilled;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbinfomessages.ConfigChange;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbinfomessages.GameInfo;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbinfomessages.InitedMessage;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbinfomessages.NavPoint;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbinfomessages.Self;
import cz.cuni.amis.pogamut.ut2004.utils.SingleUT2004BotRunner;
import cz.cuni.amis.utils.exception.PogamutException;

import bstar.bstarPlanner;

/**
 * Example of Simple Pogamut bot, that randomly walks around the map. Bot is uncapable 
 * of handling movers so far.
 *
 * @author Rudolf Kadlec aka ik
 */
@AgentScoped
public class NavigationBot extends UT2004BotModuleController {
    
    @JProp
    private NavPoint lastStuck;


    /**
     * Here we can modify initializing command for our bot.
     *
     * @return
     */
    @Override
    public Initialize getInitializeCommand() {
        return new Initialize().setName("NavigationBot");
    }

    /**
     * The bot is initilized in the environment - a physical representation of the
     * bot is present in the game.
     *
     * @param config information about configuration
     * @param init information about configuration
     */
    public NavPoint findClosestNavPoint(Collection<NavPoint> navs) {
        navs.remove(lastStuck);
        while (!navs.isEmpty()) {
            NavPoint target = DistanceUtils.getNearest(navs, bot);
            move.turnTo(target.getLocation());
            if (target.isReachable() || target.isVisible()) {
                return target;
            } else {
                navs.remove(target);
            }
        }
        return null;
    }

    @Override
    public void botInitialized(GameInfo gameInfo, ConfigChange config, InitedMessage init) {
        // add stuck detector that watch over the path-following, if it (heuristicly) finds out that the bot has stuck somewhere,
        // it reporst an appropriate path event
        pathExecutor.addStuckDetector(new StupidStuckDetector(getWorldView(), 3.0));
        pathPlanner = new bstarPlanner(bot);
        // specify what will happen when the bot reaches its destination or gets stuck
        pathExecutor.addPathListener(new PathExecutorListener() {

            public void onEvent(PathEventType eventType) {
                switch (eventType) {
                    case TARGET_REACHED:
                        // most of the time the execution will go this way
                        goToRandomNavPoint();
                        break;
                    case BOT_STUCKED:
                        // sometimes the bot gets stucked then we have to return him
                        // to some safe location, try more complex maps to get into
                        // this branche
                        //lastStuck =
                        NavPoint target = findClosestNavPoint(getWorldView().getAll(NavPoint.class).values());
                        lastStuck = target;
                        //move.jump();
                        //pathExecutor.moveTo(target.getLocation());
                        pathExecutor.followPath(pathPlanner.computePath(target));
                        break;
                }
            }
        });
    }

    @Override
    public void botSpawned(GameInfo gameInfo, ConfigChange config, InitedMessage init, Self self) {
        // start the movement
        goToRandomNavPoint();
    }

    /**
     * Main method that controls the bot - makes decisions what to do next.
     * It is called iteratively by Pogamut engine every time a synchronous batch
     * from the environment is received. This is usually 4 times per second - it
     * is affected by visionTime variable, that can be adjusted in GameBots ini file in
     * UT2004/System folder.
     *
     * @throws cz.cuni.amis.pogamut.base.exceptions.PogamutException
     */
    @Override
    public void logic() throws PogamutException {
        user.info(Integer.toString(bot.getWorldView().getSingle(Self.class).getHealth()));
        //user.info("--- Logic iteration ---");
        // log how many navpoints & items the bot knows about and which is visible
        //user.info("Visible navpoints: " + world.getAllVisible(NavPoint.class).size() + " / " + world.getAll(NavPoint.class).size());
        //user.info("Visible items:     " + world.getAllVisible(Item.class).size()     + " / " + world.getAll(Item.class).size());
    }

    /**
     * Called each time our bot die. Good for reseting all bot state dependent variables.
     *
     * @param event
     */
    @Override
    public void botKilled(BotKilled event) {
        pathExecutor.stop();
    }

    /**
     * Picks random navpoint and goes to it.
     */
    protected void goToRandomNavPoint() {
        NavPoint navPoint = pickNewRandomNavTarget();
        // find path to the random navpoint, path is computed asynchronously
        // so the handle will hold the result onlt after some time
        PathHandle<ILocated> pathHandle = pathPlanner.computePath(navPoint);
        // make the path executor follow the path, executor listens for the
        // asynchronous result of path planning
        pathExecutor.followPath(pathHandle);
    }

    /**
     * Randomly picks some navigation point to head to.
     * @return randomly choosed navpoint
     */
    private NavPoint pickNewRandomNavTarget() {
        //getLog().severe("Picking new target navpoint.");

        // 1. get all known navigation points
        Collection<NavPoint> navPoints = getWorldView().getAll(NavPoint.class).values();
        // 2. compute index of the target nav point
        int navPointIndex = random.nextInt(navPoints.size());
        // 3. find the corresponding nav point
        int i = 0;
        for (NavPoint nav : navPoints) {
            if (i == navPointIndex) {
                return nav;
            }
            i++;
        }

        // 4. deal with unexpected behavior
        throw new RuntimeException(
                "No navpoint chosen. There are no navpoints in the list of known navpoints");
    }

    public static void main(String args[]) throws PogamutException {
        new SingleUT2004BotRunner<UT2004Bot>(NavigationBot.class, "NavigationBot").startAgent();
    }
}
