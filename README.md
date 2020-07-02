# Stochastic CS:GO Economy Model

Look at `CS_ntbk` for implementation of current module `CS_EcoAnalyzer`

### Introduction

The game of Counter-Strike : Global Offensive (CSGO) is a tactical first-person-shooter (FPS) for PC whose defusal gamemode is the core of one of the largest eSports in the world. All mechanics of a competitive CSGO match can be observed in a "half". A half is divided into a predetermined number of rounds in which the attacking team (denoted the terrorists or "T") must battle the defending team (counter-terrorists or "CT") to win each round. In each round, each team starts with their 5 players alive. The objective for the T side is to either kill all 5 of the CTs *OR* plant the bomb at one of the two bombsites in the alloted round time. If the latter occurs, the CT side then have a short time window to defuse the planted bomb, and either this *OR* killing all 5 of the Ts or the time running out while at least 1 CT is still alive (before Ts have planted the bomb) leads to a win for the CTs. In a full CSGO match, two teams would play a half, each as one of the sides, and then play another half as the other side. The match is won when one of the two teams wins the maximum number of rounds in a half plus one (e.g. typical CSGO matches consist of 15 round halves and winning 16 rounds wins the match). 

One unique mechanic of CSGO is the economy system. Teams use weapons, utility and armor to win rounds, which come in varying power and prices. CSGO is an egalitarian game, thus each half all players are given the same amount of money to start the game, each round every player will start with a pistol and knife and the buying options are consistent across each side (Ts and CTs have different weaponry, but all Ts have the same and CTs have the same). Money is earned through the results of rounds (winning/losing) as well as kills and bomb interactions (plant/defuse). These are earned per player, with round rewards given equally to each player. The choice of purchase is made by each individual player (though good teams will orchestrate their decisions) and there are no characters or levels that give access to different items or prices. This makes the strategy employed with regards to managing a team's economy is a major factor in a team's likelihood of success. Not only this, but balancing the economy to be offer choice and strategy is a challenging task for developers working on the game. 

What I look to introduce is a method of exploring the ramifications of an alteration in either team's buying strategy or the fundamental economic rules (gun prices, round rewards, etc.) by simulating a stochastic process resembling the economic unfolding that occurs during a CSGO half. Because of the nature of the unfolding of the economy from initial conditions, I found it reasonable to treat the economic state as a Markov Chain. The initial conditions of the MC are what I define as the `market` (the prices of goods), the `eco_rules` (the economic parameters, some of which are a function of `market`), and the starting gamestate which just sets the framework for tracking the state of the game. These are all dictionaries, and the `eco_rules` dictionary is where most of the simulation parameters are hidden. I try to make them functions of the `market` as often as possible, but have currently hard-coded some values that need at the very least justification (specifically `force_plant_odds` and `ct_save_odds`). Other than these values, most of the mechanics are handled by the `play_round()` function wrapped in the `half_simulator()`. I will cover the implementation in more detail below, and some code documentation can be found in the module file. 


### Current Implementation



## Areas of Improvement / Notes

#### Failings   
    - teams look into other teams money for buy (handling the 'Mid-game')
    - Guessing win %s based on money invested (Could extrapolte from T1 stats)
    - Visualization/StatAnalysis Tools for handling game dictionary
    
    
#### Points to review    
    - No mixed buy possibility
    - Map/Team Parameters?
    - Using individual player economy as proxy for teams 
        = i.e. averaging out an AWPs price across team
    - Using RL to deduce optimal buying strat? 
    - Use more sophisticated eco_rules
    - Estimated buy levels based on current buys
        = should extrapolate from base prices

