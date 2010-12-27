package cz.cuni.amis.pogamut.ut2004.examples;

import java.util.LinkedList;
import java.util.List;
import java.util.Set;
import java.util.logging.Level;

import cz.cuni.amis.introspection.java.JProp;
import cz.cuni.amis.pogamut.base.agent.navigation.PathEventType;
import cz.cuni.amis.pogamut.base.agent.navigation.PathExecutorListener;
import cz.cuni.amis.pogamut.base.communication.worldview.listener.annotation.EventListener;
import cz.cuni.amis.pogamut.base.utils.guice.AgentScoped;
import cz.cuni.amis.pogamut.base.utils.math.DistanceUtils;
import cz.cuni.amis.pogamut.ut2004.agent.module.sensomotoric.Weapon;
import cz.cuni.amis.pogamut.ut2004.agent.module.utils.TabooSet;
import cz.cuni.amis.pogamut.ut2004.bot.impl.UT2004Bot;
import cz.cuni.amis.pogamut.ut2004.bot.impl.UT2004BotModuleController;
import cz.cuni.amis.pogamut.ut2004.communication.messages.ItemType;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbcommands.Initialize;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbcommands.Move;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbcommands.Rotate;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbcommands.Shoot;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbcommands.Stop;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbcommands.StopShooting;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbinfomessages.BotKilled;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbinfomessages.Item;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbinfomessages.Player;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbinfomessages.PlayerKilled;
import cz.cuni.amis.pogamut.ut2004.utils.MultipleUT2004BotRunner;
import cz.cuni.amis.utils.exception.PogamutException;

import bstar.bstarPlanner;
import cz.cuni.amis.pogamut.base.agent.navigation.PathPlanner;
import cz.cuni.amis.pogamut.base3d.worldview.object.ILocated;

/**
 * MODIFIED HUNTER BOT - All that's been changed here is the declaration:
 * PathPlanner<ILocated, ILocated> pathPlanner = new bstarPlanner(bot)
 * That replaces the use of the default pathplanner with ours.
 *
 * Example of Simple Pogamut bot, that randomly walks around the map searching for preys shooting at everything that
 * is in its way.
 *
 * @author Rudolf Kadlec aka ik
 * @author Jimmy
 * @author Benjy Cook 301173084
 */
@AgentScoped
public class Hunter extends UT2004BotModuleController<UT2004Bot> {	
    
    /** boolean switch to activate engage */
    @JProp
    public boolean shouldEngage = true;
    
    /** boolean switch to activate pursue */
    @JProp
    public boolean shouldPursue = true;
    
    /** boolean switch to activate rearm */
    @JProp
    public boolean shouldRearm = true;
    
    /** boolean switch to activate collect items */
    @JProp
    public boolean shouldCollectItems = true;
    
    /** boolean switch to activate collect health */
    @JProp
    public boolean shouldCollectHealth = true;
    
    /** how low the health level should be to start collecting healht */
    @JProp
    public int healthLevel = 90;
    
    /** how many bot the hunter killed */
    @JProp
    public int frags = 0;
    
    /** how many times the hunter died */
    @JProp
    public int deaths = 0;
    
    
    @EventListener(eventClass = PlayerKilled.class)
    public void playerKilled(PlayerKilled event) {
		if (enemy == null) return;
		if (enemy.getId().equals(event.getId())) {
			previousState = State.OTHER;
			enemy = null;
		}
	}
	    
    Player enemy = null;
    
    TabooSet<Item> tabooItems = null;

    /**
     * Bot's preparation - initialization of agent's modules take their place here.
     */
    @Override
    public void prepareBot(UT2004Bot bot) {
        tabooItems = new TabooSet<Item>(bot);

        // listeners        
        pathExecutor.addPathListener(new PathExecutorListener() {
			
			@Override
			public void onEvent(PathEventType eventType) {
				switch (eventType) {
				case BOT_STUCKED:
					if (item != null) {
						tabooItems.add(item, 10);
					}
					reset();
					break;
					
				case TARGET_REACHED:
					reset();
					break;				
				}
			}
		});        
    }
    
    /**
     * Here we can modify initializing command for our bot.
     *
     * @return
     */
    @Override
    public Initialize getInitializeCommand() {
        // just set the name of the bot, nothing else
        return new Initialize().setName("Hunter");
    }

    private static enum State {
    	OTHER,
    	ENGAGE,
    	PURSUE,
    	MEDKIT,
    	GRAB,
    	ITEMS
    }
    
    public void reset() {
    	previousState = State.OTHER;
    	notMoving = 0;
    	enemy = null;
    	pathExecutor.stop();
    	itemsToRunAround = null;
    	item = null;
    }
    
    State previousState = State.OTHER;
    
    int notMoving = 0;    
    
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
    public void logic() {
    	// global anti-stuck?
    	if (!info.isMoving()) {
    		++notMoving;
    		if (notMoving > 4) {
    			// we're stuck - reset the bot's mind
    			reset();
    		}
    	}
    	
        // 1) do you see enemy? 	-> go to PURSUE (start shooting / hunt the enemy)
        if (shouldEngage && players.canSeeEnemies() && weaponry.hasLoadedWeapon()) {
            stateEngage();            
            return;
        }

        // 2) are you shooting? 	-> stop shooting, you've lost your target
        if (info.isShooting() || info.isSecondaryShooting()) {
        	getAct().act(new StopShooting()); 
        }

        // 3) are you being shot? 	-> go to HIT (turn around - try to find your enemy)
        if (senses.isBeingDamaged()) {
        	this.stateHit();        	
        	return;
        }
        
        // 4) have you got enemy to pursue? -> go to the last position of enemy
        if (enemy != null && shouldPursue && weaponry.hasLoadedWeapon()) {  // !enemy.isVisible() because of 2)
            this.statePursue();            
            return;
        }

        // 5) are you hurt?			-> get yourself some medKit
        if (info.getHealth() < healthLevel && canRunAlongMedKit()) {
            this.stateMedKit();            
            return;
        }

        // 6) do you see item? 		-> go to GRAB_ITEM	  (pick the most suitable item and run for)        
        if (shouldCollectItems && !items.getVisibleItems().isEmpty()) {
        	stateSeeItem();
        	previousState = State.GRAB;
        	return;
        }
        
        // 7) if nothing ... run around items
        stateRunAroundItems();
    }
    
      //////////////
    //////////////////
    // STATE ENGAGE //
    //////////////////
      //////////////
    
    private boolean runningToPlayer = false;
    
    /**
     * Fired when bot see any enemy.
     * <ol>
     * <li> if enemy that was attacked last time is not visible than choose new enemy
     * <li> if out of ammo - switch to another weapon
     * <li> if enemy is reachable and the bot is far - run to him
     * <li> if enemy is not reachable - stand still (kind a silly, right? :-)
     * </ol>
     */
    private void stateEngage() {
        user.info("Decision is: ENGAGE");
        //// config.setName("Hunter [ENGAGE]");
        
        boolean shooting = false;
        double distance = Double.MAX_VALUE;
        
        // 1) pick new enemy if the old one has been lost
        if (previousState != State.ENGAGE || enemy == null || !enemy.isVisible()) {
            // pick new enemy
            enemy = players.getNearestVisiblePlayer(players.getVisibleEnemies().values());
            if (info.isShooting()) {
                // stop shooting
                getAct().act(new StopShooting());
            }
            runningToPlayer = false;        	
        }

        // 2) if out of ammo - switch to another weapon
        if (weaponry.getCurrentPrimaryAmmo() == 0 && weaponry.hasLoadedWeapon()) {
            user.info("No ammo - switching weapon");
            // obtain any loaded weapon
            Weapon weapon = weaponry.getLoadedWeapons().values().iterator().next();
            // change the weapon
            weaponry.changeWeapon(weapon);
        } else {
        	// check whether you do not have better weapon
        	Weapon currentWeapon = weaponry.getCurrentWeapon();
        	Weapon switchWeapon = null;
        	for (Weapon weapon : weaponry.getLoadedRangedWeapons().values()) {
        		if (weapon.getDescriptor().getPriDamage() > currentWeapon.getDescriptor().getPriDamage()) {
        			switchWeapon = weapon;
        		}
        	}
        	if (switchWeapon != null) {
        		weaponry.changeWeapon(switchWeapon);
        	}
        }

        if (enemy != null) {
	        // 3) if not shooting at enemyID - start shooting
	        distance = info.getLocation().getDistance(enemy.getLocation());        	             	      
	        
	        // 4) should shoot?
	        if (weaponry.getCurrentWeapon() != null) {
	            // it is worth shooting
	        	user.info("Shooting at enemy!!!");
	        	getAct().act(new Shoot().setTarget(this.enemy.getId()));
	        	shooting = true;
	        }
        }
        
        // 5) if enemy is far - run to him
        int decentDistance = Math.round(random.nextFloat() * 800) + 200;
        if (!enemy.isVisible() || !shooting || decentDistance < distance) {
        	if (!runningToPlayer) {
                        PathPlanner<ILocated, ILocated> pathPlanner = new bstarPlanner(bot);
        		pathExecutor.followPath(pathPlanner.computePath(enemy));
        		runningToPlayer = true;
        	}
        } else {
        	runningToPlayer = false;
        	pathExecutor.stop();
        	getAct().act(new Stop());
        }
        
        previousState = State.ENGAGE;
    }
    
      ///////////
    ///////////////
    // STATE HIT //
    ///////////////
      ///////////-

    protected void stateHit() {
    	user.info("Decision is: HIT");
		getAct().act(new Rotate().setAmount(32000));
		previousState = State.OTHER;
	}

      //////////////
    //////////////////
    // STATE PURSUE //
    //////////////////
      //////////////
    
    /**
     * State pursue is for pursuing enemy who was for example lost behind a corner.
     * How it works?:
     * <ol>
     * <li> initialize properties
     * <li> obtain path to the enemy
     * <li> follow the path - if it reaches the end - set lastEnemy to null - bot would have seen him before or lost him once for all
     * </ol>
     */
    protected void statePursue() {
        user.info("Decision is: PURSUE");
        //// config.setName("Hunter [PURSUE]");
        if (previousState != State.PURSUE) {
        	pursueCount = 0;
                PathPlanner<ILocated, ILocated> pathPlanner = new bstarPlanner(bot);
        	pathExecutor.followPath(pathPlanner.computePath(enemy));
        }
        ++pursueCount;
        if (pursueCount > 30) {
        	reset();      	
        } else {
        	previousState = State.PURSUE;
        }
    }
    
    int pursueCount = 0;

      //////////////
    //////////////////
    // STATE MEDKIT //
    //////////////////
      //////////////
    
    private void stateMedKit() {
    	user.info("Decision is: MEDKIT");
    	//// config.setName("Hunter [MEDKIT]");
    	if (previousState != State.MEDKIT) {
	        List<Item> healths = new LinkedList();
	        healths.addAll(items.getSpawnedItems(ItemType.HEALTH_PACK).values());
	        if (healths.size() == 0) {
	        	healths.addAll(items.getSpawnedItems(ItemType.MINI_HEALTH_PACK).values());
	        }
	        Set<Item> okHealths = tabooItems.filter(healths);
	        if (okHealths.size() == 0) {
	        	user.log(Level.WARNING, "No suitable health to run for.");
	        	stateRunAroundItems();
	        	return;
	        }
	        item = DistanceUtils.getNearest(okHealths, info.getLocation());
                PathPlanner<ILocated, ILocated> pathPlanner = new bstarPlanner(bot);
	        pathExecutor.followPath(pathPlanner.computePath(item));
    	}
    	previousState = State.MEDKIT;
    }
    
      ////////////////
    ////////////////////
    // STATE SEE ITEM //
    ////////////////////
      ////////////////
    
    Item item = null;
    
    private void stateSeeItem() {
    	user.info("Decision is: SEE ITEM");
    	//// config.setName("Hunter [SEE ITEM]");
    	
    	if (item != null && item.getLocation().getDistance(info.getLocation()) < 100) {
    		reset();
    	}
    	
    	if (previousState != State.GRAB) {
    		item = DistanceUtils.getNearest(items.getVisibleItems().values(), info.getLocation());    		
    		if (item.getLocation().getDistance(info.getLocation()) < 300) {
    			getAct().act(new Move().setFirstLocation(item.getLocation()));
    		} else {
                        PathPlanner<ILocated, ILocated> pathPlanner = new bstarPlanner(bot);
    			pathExecutor.followPath(pathPlanner.computePath(item));
    		}
    	}
    	
	}

    private boolean canRunAlongMedKit() {
    	boolean result = !items.getSpawnedItems(ItemType.HEALTH_PACK).isEmpty() ||
               		     !items.getSpawnedItems(ItemType.MINI_HEALTH_PACK).isEmpty();
    	return result;
    }

      ////////////////////////
    ////////////////////////////
    // STATE RUN AROUND ITEMS //
    ////////////////////////////
      ////////////////////////
    
    List<Item> itemsToRunAround = null;

    private void stateRunAroundItems() {    	
    	user.info("Decision is: ITEMS");
    	//// config.setName("Hunter [ITEMS]");
    	if (previousState != State.ITEMS) {
   			itemsToRunAround = new LinkedList<Item>(items.getSpawnedItems().values());
    		Set<Item> items = tabooItems.filter(itemsToRunAround);
    		if (items.size() == 0) {
    			user.log(Level.WARNING, "No item to run for...");
    			reset();
    			return;    			
    		}
    		item = items.iterator().next();
                PathPlanner<ILocated, ILocated> pathPlanner = new bstarPlanner(bot);
    		pathExecutor.followPath(pathPlanner.computePath(item));
    	}
    	previousState = State.ITEMS;
    	
    }
    
      ////////////
    ////////////////
    // BOT KILLED //
    ////////////////
      ////////////
    
    @Override
    public void botKilled(BotKilled event) {
        itemsToRunAround = null;
        enemy = null;
    }
    
////////////////////////////////////////////
////////////////////////////////////////////
////////////////////////////////////////////
    
    public static void main(String args[]) throws PogamutException {
        for (int i = 0; i < 5; i++) {
            new MultipleUT2004BotRunner<UT2004Bot>(1, Hunter.class, "SmartHunter"+Integer.toString(i)).startAgent();
        }
    }
 
}
