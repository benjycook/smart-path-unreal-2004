package bstar;

import java.util.ArrayList;
import java.util.List;
import java.util.Arrays;
import java.util.Collection;

import cz.cuni.amis.pogamut.base.utils.logging.LogCategory;
import cz.cuni.amis.pogamut.base.agent.navigation.AbstractPathHandle;
import cz.cuni.amis.pogamut.base.agent.navigation.PathHandle;
import cz.cuni.amis.pogamut.base.agent.navigation.PathNotConstructable;
import cz.cuni.amis.pogamut.base.agent.navigation.PathPlanner;
import cz.cuni.amis.pogamut.base3d.worldview.object.ILocated;
import cz.cuni.amis.pogamut.ut2004.bot.impl.UT2004Bot;
import cz.cuni.amis.pogamut.base3d.worldview.object.Location;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbinfomessages.NavPoint;
import cz.cuni.amis.pogamut.base.utils.math.DistanceUtils;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbinfomessages.Item;
import cz.cuni.amis.pogamut.ut2004.communication.messages.gbinfomessages.Player;
import java.util.Map;

import org.python.util.PythonInterpreter;

/**
 *
 * @author Benjy
 */
public class bstarPlanner implements PathPlanner<ILocated, ILocated> {

    UT2004Bot bot;
    LogCategory user;
    PythonInterpreter interp;
    Collection<NavPoint> navs;
    Collection<Player> players;
    Collection<Item> items;

    public bstarPlanner(UT2004Bot bot) {
        this.bot = bot;

        this.user = bot.getLogger().getCategory("User");
        navs = bot.getWorldView().getAll(NavPoint.class).values();
        players = bot.getWorldView().getAll(Player.class).values();
        items = bot.getWorldView().getAll(Item.class).values();
        // construcer / initalization
        // here we can create our python world
        PythonInterpreter.initialize(System.getProperties(), System.getProperties(), new String[0]);
        this.interp = new PythonInterpreter();
    }

    private Location[] runPython(NavPoint start, NavPoint to) {
        try {
            interp.set("start", start);
            interp.set("to", to);
            interp.set("navs", navs.toArray());
            interp.set("players", players.toArray());
            interp.set("items", items.toArray());
            interp.execfile("src/bstar/passArguments.py");
            interp.execfile("src/bstar/astar.py");
            return interp.get("output", Location[].class);
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    public NavPoint findClosestNavPoint() {
        NavPoint target = DistanceUtils.getNearest(navs, bot);
        return target;
    }

    public PathHandle<ILocated> computePath(final ILocated to) throws PathNotConstructable {
        //NavPoint start = DistanceUtils.getNearest(bot.getWorldView().getAllVisible(NavPoint.class).values(), bot.getWorldView().getSingle(Self.class));
        NavPoint start = findClosestNavPoint();

        // navpoints give us alot
        Location[] returnedPath;
        returnedPath = runPython(start, (NavPoint) to);
        List<Location> path = new ArrayList(Arrays.asList(returnedPath));

        return new AbstractPathHandle<ILocated>(path, true) {
            public String getTargetDescription() {
                return to.toString();
            }
        };
    }
}
