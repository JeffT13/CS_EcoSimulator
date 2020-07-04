# Stochastic CS:GO Economy Model

Look at `CS_ntbk` for implementation of current module `CS_EcoAnalyzer`

### Introduction

The game of Counter-Strike : Global Offensive (CSGO) is a tactical first-person-shooter (FPS) for PC whose defusal gamemode is the core of one of the largest eSports in the world. All mechanics of a competitive CSGO defusal match can be observed in a "half". A half is divided into a predetermined number of rounds in which the attacking team (denoted the terrorists or "T") must battle the defending team (counter-terrorists or "CT") to win each round. In each round, each team starts with their 5 players alive. The objective for the T side is to either:
    - kill all 5 of the CTs *OR* 
    - plant the bomb at one of the two bombsites in the alloted round time 
    
If the latter occurs, the CT side then have a short time window to defuse the planted bomb. Defusing a planted bomb, killing all 5 of the Ts *OR* the time running out while at least 1 CT is still alive (before Ts have planted the bomb) leads to a win for the CT side. In a full CSGO match, two teams would play a half, each as one of the sides, and then play another half as the other side. The match is won when one of the two teams wins the maximum number of rounds in a half plus one (e.g. typical CSGO matches consist of 15 round halves and winning 16 rounds wins the match). 

One unique mechanic of CSGO is the economy system. Teams use weapons, utility and armor to win rounds, which come in varying power and prices. CSGO is an egalitarian game, thus each half all players are given the same amount of money to start the game, each round every player will start with a default pistol and knife and the buying options are consistent across each side (Ts and CTs have different weaponry, but all Ts have the same and CTs have the same). Money is earned through the results of rounds (winning/losing) as well as kills and bomb interactions (plant/defuse). These are earned per player, with round rewards given equally to each player. The choice of purchase is made by each individual player (though good teams will orchestrate their decisions) and there are no characters or levels that give access to different items or prices. This makes the strategy employed with regards to managing a team's economy is a major factor in a team's likelihood of success. Not only this, but balancing the economy to be offer choice and strategy is a challenging task for developers working on the game. 

What I look to introduce is a method of exploring the ramifications of an alteration in either team's buying strategy or the fundamental economic rules (gun prices, round rewards, etc.) by simulating a stochastic process resembling the economic unfolding that occurs during a CSGO half. Because of the nature of the unfolding of the economy from initial conditions, I found it reasonable to treat the economic state as a Markov Chain. The initial conditions of the MC are what I define as the `market` (the prices of goods), the `eco_rules` (the economic parameters, some of which are a function of `market`), and the starting gamestate which just sets the framework for tracking the state of the game. These are all dictionaries, and the `eco_rules` dictionary is where most of the simulation parameters are located. I try to make them functions of the `market` as often as possible, but have currently hard-coded some values that need at the very least justification (specifically `force_plant_odds` and `ct_save_odds`). Other than these values, most of the mechanics are handled by the `play_round()` function wrapped in the `half_simulator()`. I will cover the implementation in more detail below, and some code documentation can be found in the module file `CS_EcoAnalyzer.py`. 

In `CS_ntbk` there is an implementation of the module. First you will see the MC initial conditions defined and following will be a simulation of a single half with a printout of the gamestate after every round. Below that you will see a simulation of size $n$ stored and used for statistical analysis/visualization.



### Current Implementation


First I should discuss some of the parameters I use and how I calculated them (if any calculation was used at all). The variables in question are the `t_buy_levels, ct_buy_levels, force_percent, t_win_lean, t_plant_lean, win_live_rate, force_plant_odds and ct_save_odds`. The first 5 are calculated, the last 3 are guesses currently. The T and CT buy levels are calculated using the market and what is typically considered a "full-buy" in modern professional CS:GO matches. After manually building 3 levels of buys for each (full, even, light), I realized that because of how I decide to calculate the round odds (using the money invested), T side would be penalized for having cheaper equipment, which is actually an advantage. Thus, I added a multiplier to the money invested by the T side such that if both T and CT are on their "even buy", the odds should be even as well. A similar logic was applied to the odds of Ts planting (which yields more money in the following round) and decided a seperate, larger multiplier would apply which is based on the idea that a T side with a light buy should have even odds against a CT with even buy of getting a bomb plant. This only applies to when the T side decides to buy, not force. The remaining are guesses. I assumed 40% of the team lives on any round win, which is just an attempt at guessing the average. This needs more research in both the analyzation of what actual survival rates are, as well as more complexity to add variance. Similarly, the odds for T side to plant on a force where they lose and the odds the CT side saves given T round win are guesses in which I attempt to equalize their frequency. This is non-trivial, and without doing the probability calculations I am just going to rely on running a lot of simulations and comparing estimates. Perhaps the calculations are a point of interest. With these, we can discuss the implementation of `play_round()`.
As mentioned, the `play_round()` handles most of the mechanics. This function can be essentially broken down into 3 parts. Below is the "code doc" to summarize.
        i.)  calls for teams to make a buy decision and invest
        ii.) Calculates round odds 
        iii.) PLAY:
            - Roll() and decide winner
                = if CT win
                        - calculate CT remaining money 
                        - Did Ts plant? (Buy/Force?)
                        - calculate T remaining money
                = if T win
                        - calculate T remaining money (constant player alive)
                        - Did CTs save players? (B/F irrelevant)
                        - calculate CT remaining money
             - Update loss tracker/score
             - Return round_notation
             
             
Breaking down the first part, this is a hard-coded buying strategy for each side that is implemented. It is broken up into a `buy_calc_T/CT` which decides whether to buy, save or force. The underlying logic behind the buying strategy is pretty straightfoward to any familiar with CS. If there is enough money to buy what is calculated to be the minimum buy for a side, then buy. Otherwise save unless it iss the last round, first round, or the other team also cannot buy, in which case force. I want to note here that the decision process does "cheat" and looks at the other teams money directly before the round starts, which you cannot do in CSGO (but can in Valorant for example). I found this reasonable because, especially in the 'early-game' (before the first round of both sides buying) when this mechanic occurs often, good teams do have a very good sense of the opposing economy, which is only lost track of after entering the 'mid-game' (if at all). After this decision made, it is then passed to a seocnd function `process_mny_T/CT` which returns the money invested and money remain for the side. This is also hard-coded processing and in this function, a save will cause a team to spend literally 0 dollars, a force will cause a team to spend a calculated percetnage of the team's money, and a buy will cause the team to buy at the maximum possible buy level calculated. A future prospect will be to make the `play_round()` function accept the buying strategy as an argument, as oppose to it directly calling the specified buying functions, allowing for the exploration of different buying strategies from a team. The round response variance (the amount of variance in the possible outcomes that are permitted in this iteration of `play_round()`) might need to become more robust before this would be fruitful.

After the buying decisions and money is calculated, this information is used to calculate the round odds `ct_odds` (odds the CT side wins the round) and `plant_odds` (odds the T side plants). These odds are defined as 

$$ \text{ct_odds} = \frac{\text{CT money invested}}{\text{CT money invested} + \text{t_win_lean}*\text{T money invest}} $$

$$ \text{plant_odds} = \frac{\text{CT money invested}}{\text{CT money invested} + \text{t_plant_lean}*\text{T money invest}} $$

We then use a uniform rng and use the above values as thresholds for the events that occur. The round is then processed, variables are updated and it returns a dictionary of the round in what I call `round_notation`.
    

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

