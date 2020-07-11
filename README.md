# Stochastic CS:GO Economy Simulator in Python

## Abstract

Counter-Strike : Global Offensive (CSGO) is a tactical first-person-shooter (FPS) for PC whose defusal gamemode is the core of one of the largest eSports in the world. In CSGO, the economy system dictates the tools at the disposable of otherwise essentially equal sides in each round. I propose a stochastic process modeling the economy of a CSGO half in Python which calculates the odds of winning each round, as well as other events that can take place in a round, as a function of the economic rules, the gamestate and the team economic strategy (currently static). I use this to build a Monte Carlo Markov Chain simulation which should allow for exploration of the ramifications of changes to either:
    - The economic system/ruleset in the competitive defusal gamemode CSGO  
    - The buying strategy of a team or teams. 

Disclaimer: This is a WIP. I can basically guarantee there are bugs/limitations. 

**If anyone knows reading this is familiar with how to aquire parsable CSGO match data (on pro/semi-pro teams) such as those returned in the round notation discussed at the end feel free to reach out and email me**


## Current Implementation

In `CS_ntbk` there is an implementation of the module. First you will see the MCMC initial conditions defined and following will be a simulation of a single half with a table showing the `round_notation` and `gamestate` for each round of the half. Below that you will see a simulation of size `n` (Currently 100k) stored and used for statistical analysis/visualization. Note that in the notebook there is only a call to `half_simulator()`, which is simply a wrapper for the `play_round()` function, which is where most of the actual round simulation mechanics are called. I cover how this function acts in **Methodology**. (in the doc file)

## Current Results/Speculations

Simulator seems to heavily lean towards T side winning 2nd round (~80% of the time). The mid-game seems to play out slightly in CT favor. This might be the cause of the slightly higher overall T total round win percentage (7.8/15). These stastics must be compared to current CSGO games. Is this the ramifications of the new economic changes (if even exacerbated by the simulation)? We see T side either buys or forces 2nd round 100% of the time. This is not explicitly stated in the buy logic, but is a result of the preset parameters. We also see this buy pattern implemented in T1 CSGO. 