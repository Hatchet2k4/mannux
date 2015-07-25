# Story #

For Mannux we have had a lot of different story ideas on the go. But the heart of it is really that the research station dug up something that should never have been dug up. They studied it but eventually lost control of it. This has been done before in ganes like Doom 3, Dead Space, etc. But the spin on it that we were gonna have is that as Tabby gets closer to finding out the answers to what is really going on, she gets gradually corrupted, becoming like a demon but still somehow holding on to her sense of self until the end.

The key will be preserving a feeling of isolation. This is something that has been lacking in recent Metroid and even Castlevania games, and I feel this is something we can provide to make our game appealing.

Tabitha, or Tabby, is either a mercenary, or an agent of some sort, that is called to the station, to investigate. Either as a distress call or as orders. We will need to nail this down eventually.

# Game Structure #

The world of Mannux is set within a research station that was built within an asteroid or small moon. (Not sure yet exactly what Mannux will refer to yet, whether it's the name of the station itself, the planet, or the Big Bad enemy itself). The station contains cargo/docking areas, engineering/robot manufacturing type of areas, crew quarters, medical areas and a small research lab. There is also a mining operation in place that will give the opporuntity for lots of cave areas for secrets and alternate connections to areas.

The asteroid station is also in geosynchronous orbit around a planet, connected via a large space elevator to another research station on the surface. Eventually the game will go down underground to the final areas, which may look something like a final area of Contra. It would have originally been a cave that has been overgrown with demonic/alien influence.

We can argue that the station/planet has a lower natural gravity, giving her the larger than normal jumps that she is able to make.

In the beginning areas the threats will be minimal, but give a feeling that the station is watching you. They will be mostly turrets, drones, and other small robitc enemies. Soon enough, it will be revealed that the station's AI has been corrupted, perhaps its organic components have been infected, but still has a portion that is unaffected. Tabby will set out to restore this, collecting components from certain robots that she defeats. Even at this stage though it will be hinted that there is more to it than just an out of control AI, as what look like zombies and alien beings out of research labs begin to make their appearance.

Once the AI has been restored, or at least has an isolated core that Tabby is able to construct from the collected components, it will reveal more about what has happened here. Of course not everything; there will be portions of its memory that are erased or that it is unable to access, leaving some more mystery to discover. The second half of the game will be a bit more murky...

# General Gameplay ideas #

  * Tabby is very floaty and very fast. Will need to tone this down a bit to give her a little more weight, but still feel agile.
  * First enemies will be more robotic in nature.
  * Flying Sentry drones will see you and fly away at the start, giving the feeling that the player is intruding somewhere they shouldn't be.
  * Later on these will also attack.
  * Zombies are currently in the first area, but they may work better in crew quarters areas with tighter spaces that you cannot easily jump over them.
  * Implement a Log system that we can pull from Final Eclipse, can interact with computers in the background to add them for story and background info.
    * Perhaps logs could be locked behind different access levels that you acquire, so there might be log computers that you can't open up right away but can optionally come back for them. Color coding for different access levels.
  * Doors may also have color coded lights to indicate state, lock status, etc.


  * Tabby's abilities and weapons still need to be worked on.
    * Her main weapon will be a pistol that can be upgraded to fire different types of shots. For animation sake it will just be the one style of weapon to save on drawing new frames for each new weapon.
    * Exception will be Tabby's sword. Eventually she will acquire an energy sword, and ambition permitting, a "blood" sword grown out of her own arm as she gains more demonic aspects. She will need a different sprite when in this mode.
    * Abilities may include double jumps (already implemented), slow falling/floating, dashes. We may possibly implement hanging from ledges. Wall jumping will be an earnable ability rather than be available from the start, as an enhancement to Tabby's boots.
    * All weapon upgrades will increase damage to varying degrees. The default weapon will not damage shields, but the first upgrade will cause minor shield damage. Before this the player must wait for openings to attack.
    * Boss enemies may be attackable anywhere but have a weak point which does extra damage.

  * Currently blocks break on a per tile basis, which is fine for walls, but breaking 32x32 blocks should be destroyed as if it was one large tile. Breakable blocks should usually be identifiable by a defect or crack somewhere.

# Weapons #

The pistol art on Tabby's sprite will not change directly with different weapons, however we will add a color stripe to identify the weapon mode. Swords will have custom sprite art.

Some ideas for weapons:
  * Default pistol, upgradable for increased shot size and damage. Possible to charge? Need to decide if we want to allow this. Green color stripe.
  * Rockets with limited ammo, required to destroy certain obstacles. Upgrades to a larger blast radius and splash damage. Blue color stripe.
  * Beam/Particle cannon, a sniping weapon. Powerful beam that instantly travels to its target, but relatively slow recharge rate. Upgrades to a triple beam that pierces targets but not walls. May add ammo for this weapon for balancing, if needed. Purple color stripe.
  * Flamethrower. Effective against organic enemies but relatively short range. Upgrades to a larger blast. Required to destroy alien barriers. Red color stripe.
  * Beam Saber, short ranged, but powerful weapon can destroy most regular enemies in one or two hits. ideal for skilled players the prefer more of a Castlevania style of play.
  * Blood Sword. Eventually Tabby's own arm will become a weapon, creating a sword capable of draininglife from organic enemies.

Todo: Excel sheet for damage/hp values for each weapon/enemy combination, calculating the number of hits needed to defeat for each type.

# Abilities #
  * Dash - boots upgrade, allows tabby to dash forward and make longer jumps, needed to access some new areas.
  * Double Jump - boots upgrade
  * Wall Jump - boots upgrade
  * Underwater gear for breathing in flooded areas. Further upgradable to allow for free movement in water.

# Enemies #

  * Parasite: Crawls along the floor, jumps to attack.
  * Scout: Small wheeled machine, need to crouch to destroy with the default pistol until its size has been increased.
  * Repair bot: Walking drone that cannot move quickly but can soak up a lot of damage, medium range electric shock attacks can stun Tabby.
  * Security bot: Like the repair bot, but built for combot, will fire lasers at the player and move faster.
  * Turrets: Fires three shots before recharging. Later versions may have a shield.
  * Sentry drones. Floating, shielded enemies. Laser attacks will make these dangerous.
  * Zombie: Generic mutated/corrupted crew members, they can take a few hits with the pistol but the particle beam or rocket launcher will make short work ofnthem.

# Bosses #

  * The first boss encounter will hopefully set the tone for the rest of the game, being an armored tank. Its primary attack will be rockets, followed by laser attacks from its top portion. As it takes damage, it will start launching, sentry drones. Will provide the rocket launcher upon defeat, opening more cave areas for exploration.

# Areas #

This will briefly describe each area and the items obtained in each. Interspersed within each area will be hidden cave and mining areas.

Docking/cargo area: This is where Tabby first lands. Initial objectives will be to unlock the east side, acquiring the dash boots, and opening upmsome initial cave areas.
  * Dash boots
  * Rocket launcher

Engineering/power core: The lower levels are flooded due broken coolant tanks, requiring the underwater gear to proceed.
  * Underwater gear
  * Wall jump

Crew Quarters/Research Labs
  * Flamethrower
  * Double jump

Command Deck
  * Particle beam

Space Elevator

Surface/Main Facility

Underground lake/caverns

Alien Research/Lair