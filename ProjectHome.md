My project uses the First Person Shooter video game, Unreal Tournament 2004, and an accompanying bot-programming framework, Pogamut. Pogamut allows for scripting the bots in the game, running as many as we want on a single server / game map, including human players as well. The platform also contains extensive debugging and logging services.
A`*` is used for implementing path-finding around the map for the bot, assuming his medium and long term intelligence sets a goal that is not immediately reachable. However, under the current system, the bot “naively” runs between the given way-points, following the shortest path.
My proposal is to modify this system, so that A`*` does not only take under consideration Cartesian space (i.e. shortest path), but such variables as cover, fire zones, bonuses, etc. It does this by updating the distances between way-points to reflect not only space, but tactical viability in general. The project itself will only effect the low level implementation of A`*`. In other words, any bot programmed can choose to use this modification, without it affecting the other parts of its medium or high level intelligence. In addition to the modularity of the code, it is designed to be lightweight, with the heavier calculations (such as map anaylsis) being carried out offline, while the real-time processing is designed to be no heavier than the A`*` search already being carried out.

Original Proposal: http://smart-path-unreal-2004.googlecode.com/files/Proposal.pdf

---

Project Presentation:
http://smart-path-unreal-2004.googlecode.com/files/Street%20Smarts.pptx (ppt 07)
http://smart-path-unreal-2004.googlecode.com/files/Street%2520Smarts.pdf (PDF)

---

Gameplay Video: http://www.vimeo.com/18221321