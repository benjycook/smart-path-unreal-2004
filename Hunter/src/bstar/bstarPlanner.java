package bstar;

import java.util.ArrayList;
import java.util.List;
import java.util.Arrays;

import cz.cuni.amis.pogamut.base.utils.logging.LogCategory;
import cz.cuni.amis.pogamut.base.agent.navigation.AbstractPathHandle;
import cz.cuni.amis.pogamut.base.agent.navigation.PathHandle;
import cz.cuni.amis.pogamut.base.agent.navigation.PathNotConstructable;
import cz.cuni.amis.pogamut.base.agent.navigation.PathPlanner;
import cz.cuni.amis.pogamut.base.communication.worldview.object.IWorldObject;
import cz.cuni.amis.pogamut.base3d.worldview.object.ILocated;
import cz.cuni.amis.pogamut.ut2004.bot.impl.UT2004Bot;
import cz.cuni.amis.pogamut.base3d.worldview.object.Location;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbinfomessages.NavPoint;
import cz.cuni.amis.pogamut.base.utils.math.DistanceUtils;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbinfomessages.Item;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbinfomessages.Player;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbinfomessages.Self;

import org.python.util.PythonInterpreter;



/**
 * The Java module that interfaces between the A* in python and the
 * Pogamut code.
 * @author Benjy
 */
public class bstarPlanner implements PathPlanner<ILocated, ILocated> {

    UT2004Bot bot;
    LogCategory user;
    PythonInterpreter interp;
    NavPoint[] navs;
    Player[] players;
    Item[] items;
    Self self;
    IWorldObject gun;

    public bstarPlanner(UT2004Bot bot) {
        this.bot = bot;
        this.user = bot.getLogger().getCategory("User");
        updateData();
        // construcer / initalization
        // here we can create our python world
        PythonInterpreter.initialize(System.getProperties(), System.getProperties(), new String[0]);
        this.interp = new PythonInterpreter();
    }

    private Location[] runPython(NavPoint start, NavPoint to) {
        try {
            updateData();
            interp.set("start", start);
            interp.set("to", to);
            interp.set("navs", navs);
            interp.set("players", players);
            interp.set("items", items);
            interp.set("me", self);
            interp.execfile("src/bstar/passArguments.py");
            interp.execfile("src/bstar/astar.py");
            return interp.get("output", Location[].class);
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    public NavPoint findClosestNavPoint(ILocated pt) {
        List<NavPoint> navlist = Arrays.asList(navs);
        NavPoint target = DistanceUtils.getNearest(navlist, pt);
        return target;
    }

    public PathHandle<ILocated> computePath(final ILocated to) throws PathNotConstructable {
        //NavPoint start = DistanceUtils.getNearest(bot.getWorldView().getAllVisible(NavPoint.class).values(), bot.getWorldView().getSingle(Self.class));
        NavPoint start = findClosestNavPoint(bot.getLocation());
        NavPoint toNav = findClosestNavPoint(to);
        // navpoints give us alot
        Location[] returnedPath;
        returnedPath = runPython(start, toNav);
        List<Location> path = new ArrayList(Arrays.asList(returnedPath));
        path.add(to.getLocation());

        return new AbstractPathHandle<ILocated>(path, true) {
            public String getTargetDescription() {
                return to.toString();
            }
        };
    }

    private void updateData() {
        this.navs = new NavPoint[bot.getWorldView().getAll(NavPoint.class).size()];
        this.players = new Player[bot.getWorldView().getAll(Player.class).size()];
        this.items = new Item[bot.getWorldView().getAll(Item.class).size()];
        this.self = bot.getWorldView().getSingle(Self.class);
        bot.getWorldView().getAll(NavPoint.class).values().toArray(navs);
        bot.getWorldView().getAll(Player.class).values().toArray(players);
        bot.getWorldView().getAll(Item.class).values().toArray(items);
    }
}
