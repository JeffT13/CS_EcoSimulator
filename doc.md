# Stochastic CS:GO Economy Simulator in Python

### Main Documentation

---

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

I propose a stochastic process modeling the economy of a CSGO half in Python which calculates the odds of winning each round, as well as other events that can take place in a round, as a function of the economic rules, the gamestate and the team economic strategy (currently static). I use this to build a Monte Carlo Markov Chain simulation which should allow for analysis of the ramifications of either changes to the economic system/ruleset in CSGO or the buying strategy of a team or teams.

The initial conditions of the MCMC fundamentally are the economic rules (`eco_rules`) and the gamestate. I define the gamestate as each teams' money, loss counter and the score. The economic rules contains what I call the `market` (the price of all purchasable goods), as well as predefined values such as round win/loss rewards, starting money, max money, max loss, etc. Also in the economic rules are values calculated based on the market/my intuitions regarding the game/statistical analysis which impact the liklihood of different events occuring in a round, or more specifically what I expect to be the average return over time. An area of further research is making some of these values random variables as oppose to even calculated statistics or ratios, allowing for more variance and complexity. Technically the chain is also a function of the buying strategy, and thus the buying strategy would also an initial condition. Currently, this process is hard-coded into the simulation, and so I do not treat is as a parameter. These two ideas are main areas of investigation and discussed in slightly more depth later on.

In `CS_ntbk` there is an implementation of the module. First you will see the MCMC initial conditions defined and following will be a simulation of a single half with a table showing the `round_notation` and `gamestate` for each round of the half. Below that you will see a simulation of size $n$ stored and used for statistical analysis/visualization. Note that in the notebook there is only a call to `half_simulator()`, which is simply a wrapper for the `play_round()` function, which is where most of the actual round simulation mechanics are called. I cover how this function acts in **Methodology**. 

## Methodology

Firstly, I should discuss some of the parameters I use and how I calculated them (if any calculation was used at all). These values are all found in the notebook and some of their mathematical representations* are shown in the first cell. They are:
    - `t_buy_levels 
    - ct_buy_levels 
    - t_win_lean* 
    - t_plant_lean* 
    - force_rate* 
    - win_LR_kill
    - win_LR_obj
    - win_LR_save
    - save_returnrate` 
    
The buy levels are lists which contain what I define as the minimum, maximum and even buy for each side. The maximum buy is the most a team can invest into a single round and the minimum is the lowest price of a buy before it is categorized as a "force". The percentage of your money that is spent when forcing is the price of a vest (most common pistol round buy) over the player starting money. I found the most straightforward method of handling pistol round buying is to simply demand every player spend a predetermined percentage of their money. I then found it fair to call this purchase a "force" and thus imply the `force_rate`. As an avid CSGO player I find this one of the more "poetic" relationships. Also to note, this means saving on pistol round is not a possible strategy for the simulation, but is an area of investigation. I use the even buy value for each side as the metric to equate the round winning probability, to compensate for unequal pricing. Since the T side has cheaper equipment of equal or greater power, I add a multiplier called the "t_lean" to what the T side invests before calculating the odds of the teams winning or the bomb being planted. This calls for 2 leans, "win" and "plant", as the dictionary shows. This is because planting does not necessitate a win for the T side. The economic ramifications of the events following a decision are static. The "win_LR" values are the rates of players alive after winning a round given different round circumstances (win by kill, win by obj, win against save) that the round simulator allows, and technically there is a lose liverate, but it is built in. These are calculated based on my guess of what ends up being saved on average against buys/forces under scenarios, and I use market prices and buy levels to tie them to the economy. I will discuess the save return reate more deeply later on. Converting the economic result of events to RVs is an area of further investigation.
 Converting the economic result of events to RVs is an area of further investigation. as well as justifying the save return rate are main areas of further investigation. I will mention this again  

(One idea is to tie the saving characteristics to a per-team risk-adversity and the possible buy in the future. This would have to impact the `ct_odds` as well as plant odds. Would this be implemented on a per round level? Or on the whole of the game?)


With these, we can discuss the implementation of `play_round()`.
As mentioned, the `play_round()` handles most of the mechanics. This function can be essentially broken down into 3 parts. Below is the "code doc" (also found in the .py file) to summarize.
        i.)  calls for teams to make a buy decision and invest
            ii.) Calculates round odds 
            iii.) PLAY:
                - Roll() and decide winner
                    - use roll odds to determine if plant occured
                    - Consider buys and odds to determine ending economics
                    - Consider saving by CT if Ts win (on CT buys only)
                 - Update loss tracker/score
                 - Return round_notation
             
             
Breaking down the first part, this is a hard-coded buying strategy for each side that is implemented. It is broken up into a `buy_calc_T/CT` which decides whether to buy, save or force. The underlying logic behind the buying strategy is pretty straightfoward to any familiar with CS. If there is enough money to buy what is calculated to be the minimum buy for a side, then buy. Otherwise save unless it is the last round, first round, or the other team also cannot buy, in which case force. I want to note here that the decision process does "cheat" and looks at the other teams money directly before the round starts, which you cannot do in CSGO (but can in Valorant for example). I found this reasonable because, especially in the *early-game* (before the first round of both sides buying) when this mechanic occurs often, good teams do have a very good sense of the opposing economy, which is only lost track of after entering the *mid-game* (if at all). 

After this decision is made, it is then passed to a second function `process_mny_T/CT` which returns the money invested and money remain for the side. This is also hard-coded processing and in this function, a save will cause a team to spend literally 0 dollars, a force will cause a team to spend a calculated percetnage of the team's money, and a buy will cause the team to buy at the maximum possible buy level calculated. A future prospect will be to make the `play_round()` function accept the buying strategy as an argument, as oppose to it directly calling the specified buying functions, allowing for the exploration of different buying strategies from a team. I think the money processing methodology is somewhat robust, such that if someone wanted to add their own buying strategy (essentially a function that take the gamestate and economic rules and outputs one of the possible economic decisions "buy-force-save". One could theoretically add buy levels and a different force rate (even per side), though it is unclear yet how sensitive the simulation would be to that. The round response variance (the amount of variance in the possible outcomes that are permitted in this iteration of `play_round()`) might need to become more robust before this would be truly fruitful.

After the buying decisions and money is calculated, this information is used to calculate the round odds `ct_odds` (odds the CT side wins the round) and `plant_odds` (odds the T side plants). These odds are defined in the first cell of the notebook. The values act as thresholds for a uniform rng to decide the events that occur. After using the `ct_odds` to decide a winner, the `plant_odds` is used to determine if the round was won by kills or objective. This ratio is an area of further investigation. 

In CSGO, there is the option to hold on to your buy (commonly called "saving", but since I have named saving a buying decision, I try to refrain from using the word to describe this mechanic in my writing aside from when in quotes), that is stay alive and keep the guns you purchased in the current round for the next round (even in the case of a loss). Technically both sides can do this, but when a T side hold on to their buy(if the bomb was not planted), they would not receive their loss reward (somewhat balancing out the financial benefit of doing so). Because of this, I only consider the ramifications of if the CT side "saves" *when they buy* (which is much more popular on full buy rounds). To handle this, the "save" return rate is currently a guess that I did not tie to even the economy and I just assume that on average 1 person lives on a save per save, who tends to save an awp and util (AWPs are extremely popular to hold on to given their price and power). This values tries to be the average percent of money held on to under all scenarios. In reality, this is not a plausible statistic, even with parsable data. This percentage, and really the whole "saving" mechanic, is maybe the largest areasof investigation.


With all of this, it covers at least the most popular events that occur in a CSGO match along with estimations or deductions of their ramifications. Events occuring update the teams' money accordingly, and track if an event occurs. The round is then processed, variables are updated and it returns a dictionary of the round in what I call `round_notation` which also holds the `gamestate`. Formats below:

     - gamestate = {'ct_mny': CT Money Remaining,
                        'ct_loss': CT Loss Counter,
                        't_mny': T Money Remaining,
                        't_loss': T Loss Counter,
                        't_wins': T Rounds Won,
                        'rnds_played': Rounds Played }
                        
    - round_notation = {'winner': round winner,
                        'event': bomb_plant OR none,
                        'CT_mnyinvest': CT Money Invested, 
                        'CT_buyoption': CT Buy Decision,
                        'T_mnyinvest': T Money Invested, 
                        'T_buyoption': T Buy Decision, 
                        'gamestate':   Current gamestate}

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
