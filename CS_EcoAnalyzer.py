#!\usr\bin\python


'''
Below are the functions which hold the logic to utilize the above parameters. 

The buy logic implemented by the teams is outlined below. This is the area where a team would look to explore strategies given some of the above parameters. This is also what a RL algo might replace.

This is the main implementation of the CS_EcoAnalyzer module

'''

import numpy as np
import random



def calc_expectedloss(eco_rules, gamestate, side):
    ''' 
    returns the expected loss reward to be received following a loss in the round to take place
    '''
    if side.lower()=='ct':
        loss = min(gamestate['ct_loss']+1, eco_rules['max_loss'])
        return (loss*eco_rules['loss_increment'])+eco_rules['loss_reward']
    elif side.lower()=='t':
        loss = min(gamestate['t_loss']+1, eco_rules['max_loss'])
        return (loss*eco_rules['loss_increment'])+eco_rules['loss_reward']
    else:
        print("Invalid Side")
        return 

 
'''
    Hard-Coded buying strategy for CT/T side
    Essentially the same for both sides.
    Looks into opposing teams money to prevent dual-saves.
    Assumes hard minimum for "Buy" defined in presets
'''

def buy_calc_CT(eco_rules, gamestate):    
    if gamestate['ct_mny']>= min(eco_rules['ct_bl']):
            dec_CT = 'B'
    else:
        if (gamestate['rnds_played']==0 or (gamestate['rnds_played']==eco_rules['MR']-1)):
            dec_CT = 'F'
        elif ((gamestate['ct_mny'] + calc_expectedloss(eco_rules, gamestate, 'ct')>=min(eco_rules['ct_bl']))
              and 
              (gamestate['t_mny']>= min(eco_rules['t_bl']))):
            dec_CT = 'S'
        else:
            dec_CT = 'F'
    return dec_CT
             
                          
def buy_calc_T(eco_rules, gamestate):
    if gamestate['t_mny']>= min(eco_rules['t_bl']):
            dec_T = 'B'
    else:
        if (gamestate['rnds_played']==0 or (gamestate['rnds_played']==eco_rules['MR']-1)):
             dec_T = 'F'
        elif ((gamestate['t_mny'] + calc_expectedloss(eco_rules, gamestate, 't')>=min(eco_rules['t_bl']))
              and 
              (gamestate['ct_mny']>= min(eco_rules['ct_bl']))):
            dec_T = 'S'
        else:
            dec_T = 'F'
    return dec_T
             
 


'''Processes buy decision for a team'''    
def process_mny_CT(eco_rules, gamestate, decision):
    if decision=='B':
        mny_invest = max([val for val in eco_rules['ct_bl'] if gamestate['ct_mny'] >= val])
        mny_remain = gamestate['ct_mny']- mny_invest
    if decision=='F':
        mny_invest = round(gamestate['ct_mny']*eco_rules['force_rate'], 0)
        mny_remain = gamestate['ct_mny']- mny_invest
    if decision=='S':
        mny_invest = 0
        mny_remain = gamestate['ct_mny']
    return [mny_invest, mny_remain]

 
    
def process_mny_T(eco_rules, gamestate, decision):
    if decision=='B':
        mny_invest = max([val for val in eco_rules['t_bl'] if gamestate['t_mny'] >= val])
        mny_remain = gamestate['t_mny']- mny_invest
    if decision=='F':
        mny_invest = round(gamestate['t_mny']*eco_rules['force_rate'], 0)
        mny_remain = gamestate['t_mny']- mny_invest
    if decision=='S': 
        mny_invest = 0
        mny_remain = gamestate['t_mny']
    return [mny_invest, mny_remain]
      
      


        
def play_round(eco_rules, gamestate):
            
    '''
        Main function of CS_EcoAnalyze Module:
            i.)  calls for teams to make a buy decision and invest
            ii.) Calculates round odds 
            iii.) PLAY:
                - Roll() and decide winner
                    - use roll odds to determine if plant occured
                    - Consider buys and odds to determine ending economics
                    - Consider saving by CT if Ts win (on buys only)
                 - Update loss tracker/score
                 - Return round_notation
    '''
    
    #Manage Economy
    t = buy_calc_T(eco_rules, gamestate)
    ct = buy_calc_CT(eco_rules, gamestate)
    t_eco = process_mny_T(eco_rules, gamestate, t)
    ct_eco = process_mny_CT(eco_rules, gamestate, ct)
    
    #Establish Odds of CT winning round / T plant 
    ct_odds = (ct_eco[0]+1)/(t_eco[0]*eco_rules.get('t_win_lean', 1) + ct_eco[0]) #save ~guarantees loss
    plant_odds = (ct_eco[0]+1)/(t_eco[0]*eco_rules.get('t_plant_lean', 1) + ct_eco[0])

    #PLAY (no eco wins)
    roll = random.random()
    if roll<ct_odds:
        winner='CT'

        #Bomb Plant?
        if t=='B':
            if roll<((eco_rules['t_win_lean']*ct_odds)-plant_odds):
                event = 'bomb_plant_buy'
                ct_eco[1] = min(ct_eco[1] + eco_rules['win_reward_obj'] + eco_rules['kill_reward'] + round(ct_eco[0]*eco_rules['win_LR_obj']), eco_rules['max_mny'])
                t_eco[1] = min(t_eco[1] + calc_expectedloss(eco_rules, gamestate, 't') + eco_rules['plant_reward'] + eco_rules['kill_reward'], eco_rules['max_mny'])
            else:
                event = 'none'
                ct_eco[1] = min(ct_eco[1] + eco_rules['win_reward_kill'] + eco_rules['kill_reward'] + round(ct_eco[0]*eco_rules['win_LR_kill']), eco_rules['max_mny'])
                t_eco[1] =  min(t_eco[1] + calc_expectedloss(eco_rules, gamestate, 't') + eco_rules['kill_reward']*(2/3), eco_rules['max_mny'])
                
        elif t=='F':
            if roll<(ct_odds-plant_odds):
                event='bomb_plant_force'
                ct_eco[1] = min(ct_eco[1] + eco_rules['win_reward_obj'] + eco_rules['kill_reward'] + round(ct_eco[0]*eco_rules['win_LR_obj']), eco_rules['max_mny'])
                t_eco[1] = min(t_eco[1] + calc_expectedloss(eco_rules, gamestate, 't') + eco_rules['plant_reward'] + eco_rules['kill_reward'], eco_rules['max_mny'])
            else:
                event = 'none'
                ct_eco[1] = min(ct_eco[1] + eco_rules['win_reward_kill'] + eco_rules['kill_reward'] + round(ct_eco[0]*eco_rules['win_LR_kill']), eco_rules['max_mny'])
                t_eco[1] =  min(t_eco[1] + calc_expectedloss(eco_rules, gamestate, 't') + eco_rules['kill_reward']*(1/3), eco_rules['max_mny'])

        else:
            event = 'none'
            ct_eco[1] = min(ct_eco[1] + eco_rules['win_reward_kill'] + eco_rules['kill_reward'] + round(ct_eco[0]*eco_rules['win_LR_save']), eco_rules['max_mny'])
            t_eco[1] =  min(t_eco[1] + calc_expectedloss(eco_rules, gamestate, 't'), eco_rules['max_mny'])

        #Manage Loss/Score
        ct_l = max(gamestate['ct_loss']-1,0)
        t_l = min(gamestate['t_loss']+1, eco_rules['max_loss'])
        t_w = gamestate['t_wins']
        evt = event
        
    else:
        winner='T'
        
        # Bomb Plant?
        if roll>(1-(plant_odds/eco_rules['t_win_lean'])):
            event = "bomb_plant"
            t_eco[1] = min(t_eco[1] + eco_rules['win_reward_obj'] + eco_rules['kill_reward'] + round(t_eco[0]*eco_rules['win_LR_obj']), eco_rules['max_mny'])
            if ct=='B':
                ct_eco[1] = min(ct_eco[1] + calc_expectedloss(eco_rules, gamestate, 'ct') + ct_eco[0]*eco_rules['save_returnrate'], eco_rules['max_mny'])
            else:
                ct_eco[1] = min(ct_eco[1] + calc_expectedloss(eco_rules, gamestate, 'ct'), eco_rules['max_mny'])
        else:
            event = 'none'
            t_eco[1] = min(t_eco[1] + eco_rules['win_reward_kill'] + eco_rules['kill_reward'] + round(t_eco[0]*eco_rules['win_LR_kill']), eco_rules['max_mny'])
            ct_eco[1] = min(ct_eco[1] + calc_expectedloss(eco_rules, gamestate, 'ct'), eco_rules['max_mny'])
        
        t_l  = max(gamestate['t_loss']-1,0)
        ct_l = min(gamestate['ct_loss']+1, eco_rules['max_loss'])
        t_w  = gamestate['t_wins']+1
        evt = event

    
    #Update Values
    new_gamestate = {'ct_mny': ct_eco[1],
                        'ct_loss': ct_l,
                        't_mny': t_eco[1],
                        't_loss': t_l,
                        't_wins': t_w,
                        'rnds_played': gamestate['rnds_played']+1
                }
                
    round_notation = {'winner': winner,
                        'event': evt,
                        'CT_mnyinvest': ct_eco[0], 
                        'CT_buyoption':ct,
                        'T_mnyinvest': t_eco[0], 
                        'T_buyoption': t, 
                        'gamestate': new_gamestate,
                }
    return round_notation
    
    
def half_simulator(eco_rules, preset_gamestate, n):
    half_dict = {}

    for i in range(n):
        gamestate = preset_gamestate
        half_dict[i] = []
        for j in range(eco_rules['MR']):
            rn = play_round(eco_rules, gamestate)
            gamestate = rn['gamestate']
            half_dict[i].append(rn)            
    return half_dict
