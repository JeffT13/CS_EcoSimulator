# Stochastic CS:GO Economy Simulator in Python

## Abstract

Counter-Strike : Global Offensive (CSGO) is a tactical first-person-shooter (FPS) for PC whose defusal gamemode is the core of one of the largest eSports in the world. In CSGO, the economy system dictates the tools at the disposable of otherwise essentially equal sides in each round. I propose a stochastic process modeling the economy of a CSGO half in Python which calculates the odds of winning each round, as well as other events that can take place in a round, as a function of the economic rules, the gamestate and the team economic strategy. I use this to build a Monte Carlo Markov Chain simulation which should allow for exploration of the ramifications of changes to either:
    - The economic system/ruleset in the competitive defusal gamemode CSGO  
    - The buying strategy of a team or teams. 

Disclaimer: This is a WIP. In some of the writing I write what I plan to do as if I have done it. 


## Introduction


#### Why Counter-Strike : Global Offensive?

Counter-Strike : Global Offensive (CSGO) is a tactical first-person-shooter (FPS) for PC whose defusal gamemode is the core of one of the largest eSports in the world. All mechanics of a competitive CSGO defusal match can be observed in a "half". A half is divided into a predetermined number of rounds in which the attacking team (denoted the terrorists or "T") must battle the defending team (counter-terrorists or "CT") to win each round. In each round, each team starts with their 5 players alive. The objective for the T side is to either:
    - kill all 5 of the CTs *OR* 
    - plant the bomb at one of the two bombsites in the alloted round time 
    
If the latter occurs, the CT side then have a short time window to defuse the planted bomb. Thus the CT side wins by either:
    - Defusing a planted bomb
    - killing all 5 of the Ts *OR* 
    - The time running out while at least 1 CT is still alive (before Ts have planted the bomb)
    
In a full CSGO match, two teams would play a half, each as one of the sides, and then play another half as the other side. The match is won when one of the two teams wins the maximum number of rounds in a half plus one (e.g. typical CSGO matches consist of 15 round halves and winning 16 rounds wins the match). 

One unique mechanic of CSGO is the economy system. Teams use weapons, utility and armor to win rounds, which come in varying power and prices. The economy system dictates how players proceed to gain and use money on these tools. CSGO is an egalitarian game, thus each half all players are given the same amount of money to start the half, each round every player will start with a default pistol (which is quite weak) and knife and the buying options are consistent across each side (Ts and CTs have different weaponry, but all Ts have the same and CTs have the same). Money is earned through the results of rounds (winning/losing) as well as kills and bomb interactions (plant/defuse). These are earned per player, with round rewards given equally to each player. The choice of purchase is made by each individual player (though good teams will orchestrate their decisions) and there are no characters or levels that give access to different items or prices. This makes the strategy employed with regards to managing a team's economy is a major factor in a team's likelihood of success. Not only this, but balancing the economy to offer choice and strategy is a challenging task for developers working on the game. 

#### What is all this?

I propose a stochastic process modeling the economy of a CSGO half in Python which calculates the odds of winning each round, as well as other events that can take place in a round, as a function of the economic rules, the gamestate and the team economic strategy. I use this to build a Monte Carlo Markov Chain simulation which should allow for analysis of the ramifications of either changes to the economic system/ruleset in CSGO or the buying strategy of a team or teams.

The initial conditions of the MCMC fundamentally are the economic rules (`eco_rules`) and the gamestate. I define the gamestate as each teams' money, loss counter and the score. The economic rules contains what I call the `market` (the price of all purchasable goods), as well as predefined values such as round win/loss rewards, starting money, max money, max loss, etc. Also in the economic rules are values calculated based on the market/my intuitions regarding the game/statistical analysis which impact the liklihood of different events occuring in a round, or more specifically what I expect to be the average return over time. An area of further research is making some of these values random variables as oppose to even calculated statistics, allowing for more variance. Overall this is a main area of investigation.. Technically the chain is also a function of the buying strategy, and thus the buying strategy is also an initial condition. Currently, this process is hard-coded into the simulation, and so not a parameter.

In `CS_ntbk` there is an implementation of the module. First you will see the MCMC initial conditions defined and following will be a simulation of a single half with a printout of the gamestate after every round (this is shown as a table in the notebook as well). Below that you will see a simulation of size $n$ stored and used for statistical analysis/visualization. Note that in the notebook there is only a call to `half_simulator()`, which is simply a wrapper for the `play_round()` function, which is where most of the actual round simulation mechanics are called. I talk about this more deeply in **Methodology**. 


## Methodology

Firstly, I should discuss some of the parameters I use and how I calculated them (if any calculation was used at all). The variables in question are the `t_buy_levels, ct_buy_levels, force_percent, t_win_lean, t_plant_lean, win_live_rate, force_plant_odds and ct_save_odds`. The first 5 are calculated, the last 3 are guesses currently. The T and CT buy levels are calculated using the market and what is typically considered a "full-buy" in modern professional CS:GO matches. After manually building 3 levels of buys for each (full, even, light), I realized that because of how I decide to calculate the round odds (using the money invested), T side would be penalized for having cheaper equipment, which is actually an advantage. Thus, I added a multiplier to the money invested by the T side such that if both T and CT are on their "even buy", the odds should be even as well. A similar logic was applied to the odds of the T side planting (which yields more money in the following round) and decided a seperate, larger multiplier would apply which is based on the idea that a T side with a light buy should have even odds against a CT with even buy of getting a bomb plant. This only applies to when the T side decides to buy, not force. The remaining are guesses. I assumed 40% of the team lives on any round win, which is just an attempt at guessing the average. This needs more research in both the analyzation of what actual survival rates are, as well as more complexity to add variance. Similarly, the odds for T side to plant on a force where they lose and the odds the CT side saves given T round win are guesses in which I attempt to equalize their frequency. This is non-trivial, and without doing the probability calculations I am just going to rely on running a lot of simulations and comparing estimates. Perhaps the calculations are a point of interest.

With these, we can discuss the implementation of `play_round()`.
As mentioned, the `play_round()` handles most of the mechanics. This function can be essentially broken down into 3 parts. Below is the "code doc" (also found in the .py file) to summarize.
        i.)  calls for teams to make a buy decision and invest
        ii.) Calculates round odds 
        iii.) PLAY:
            - Roll() and decide winner
                = if CT win
                        - calculate CT remaining money (constant player alive)
                        - Did Ts plant? (Buy/Force?)
                        - calculate T remaining money
                = if T win
                        - calculate T remaining money (constant player alive)
                        - Did CTs save players? (B/F irrelevant)
                        - calculate CT remaining money
             - Update loss tracker/score
             - Return round_notation
             
             
Breaking down the first part, this is a hard-coded buying strategy for each side that is implemented. It is broken up into a `buy_calc_T/CT` which decides whether to buy, save or force. The underlying logic behind the buying strategy is pretty straightfoward to any familiar with CS. If there is enough money to buy what is calculated to be the minimum buy for a side, then buy. Otherwise save unless it is the last round, first round, or the other team also cannot buy, in which case force. I want to note here that the decision process does "cheat" and looks at the other teams money directly before the round starts, which you cannot do in CSGO (but can in Valorant for example). I found this reasonable because, especially in the 'early-game' (before the first round of both sides buying) when this mechanic occurs often, good teams do have a very good sense of the opposing economy, which is only lost track of after entering the 'mid-game' (if at all). After this decision made, it is then passed to a seocnd function `process_mny_T/CT` which returns the money invested and money remain for the side. This is also hard-coded processing and in this function, a save will cause a team to spend literally 0 dollars, a force will cause a team to spend a calculated percetnage of the team's money, and a buy will cause the team to buy at the maximum possible buy level calculated. A future prospect will be to make the `play_round()` function accept the buying strategy as an argument, as oppose to it directly calling the specified buying functions, allowing for the exploration of different buying strategies from a team. The round response variance (the amount of variance in the possible outcomes that are permitted in this iteration of `play_round()`) might need to become more robust before this would be fruitful.

After the buying decisions and money is calculated, this information is used to calculate the round odds `ct_odds` (odds the CT side wins the round) and `plant_odds` (odds the T side plants). These odds are defined as 

$$ \text{ct_odds} = \frac{\text{CT money invested}}{\text{CT money invested} + \text{t_win_lean}*\text{T money invest}} $$

$$ \text{plant_odds} = \frac{\text{CT money invested}}{\text{CT money invested} + \text{t_plant_lean}*\text{T money invest}} $$

We then use a uniform rng and use the above values as thresholds for the events that occur. The round is then processed, variables are updated and it returns a dictionary of the round in what I call `round_notation`.
    

## Notes


Anything under failing is something that needs to be addressed to call the project complete. Points to review are nice additions/considerations at a future date.

#### Failings   
    - More Robust Economy (accept complexity)
        = Eco buying
        = Variance in PLayers surviving
        = "Stealing" (saving guns you didnt buy)
        = Kill/Plant Reward
        = T Saving/ CT Double Save?
    - Visualization/StatAnalysis Tools for handling game dictionary]
    - Compare Simulation Results to (preferably) T1 Pro stats
    
    
#### Points to review
    - Add Parameters
        - Map
        - Buying Strat
    - teams look into other teams money for buy (handling the 'Mid-game')
    - No mixed buy possibility
    - Using individual player economy as proxy for teams 
        = i.e. averaging out an AWPs price across team
    - Using RL to deduce optimal buying strat? 
    - Use more sophisticated eco_rules
    - Estimated buy levels based on current buys
        = should extrapolate from base prices

