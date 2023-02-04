from arrangement import *
from game import *
from card import *

def draw(hand, top_discard, last_turn, picked_up_discard_cards, player_position, wildcard_rank, num_turns_this_round):
    """
    (list,int,bool,list,int,int,int) -> str
    
    Decides from where to pick a card between the discard pile and the stock pile
    based on the top_discard card that is face up and the possible arrangements in the player’s
    hand. Returns ‘discard’ or ‘stock’ as a string.
    
    >>> draw([1,2],3,False,[[5],[6],[7]],1,7,2)
    Hand: TWO of HEARTS, TWO of DIAMONDS
    'discard'
    >>> draw([1,2],25,False,[[5],[6],[7]],1,6,2)
    Hand: TWO of HEARTS, TWO of DIAMONDS
    'discard'
    >>> draw([1,2],31,False,[[5],[6],[7]],1,6,2)
    draw([1,2],31,False,[[5],[6],[7]],1,6,2)
    'stock'
    """
    
    
    #first check if the top_discard has rank equals to wildcard_rank
    #if so,we want to draw top_discard
    if get_rank(top_discard)==wildcard_rank:
        return "discard"
    
    #then check whether drawing the top_discard can help us have better arrangements
    #which means have fewer penalty points
    #if so,we want to draw top_discard
    
    new_hand=hand+[top_discard]
    
    #use get_arrangement to check for best arrangement
    #once for the original hand,another time for hand with top_discard
    hand_arrangement=get_arrangement(tuple(hand),wildcard_rank)
    new_hand_arrangement=get_arrangement(tuple(new_hand),wildcard_rank)
    
    #remove all the arrangements in our hand,then calculate penalty points
    for arrangement in hand_arrangement:
        for card in arrangement:
            hand.remove(card)
    for arrangement in new_hand_arrangement:
        for card in arrangement:
            new_hand.remove(card)
    
    #use calculate_round_points to calculate penalty points
    hand_score=calculate_round_points(hand)
    new_hand_score=calculate_round_points(new_hand)
    
    #if drawing top_discard can help us have fewer penalty points
    #then we draw top_discard
    if new_hand_score < hand_score:
        return "discard"
    
    
    #after checking for arrangements,
    #we want to check if top_discard's rank equals to one of the cards' rank in our hand
    #for example,we now have rank:5,6,7,and top_discard has rank 5
    #although drawing top_discard cannot directly help us going out in this turn
    #we can still draw rank 5 and discard rank 7 later,
    #which help us have fewer penalty points.
    rank=[]
    for card in hand:
        rank.append(get_rank(card))
    
    for a_rank in rank:
        #penalty points are too large for 8,9,10,jack,queen and king,
        #as you cannot directly form an arrangememnt in this turn
        #you may not want to keep them
        if get_rank(top_discard)==a_rank and a_rank !=(6 or 7 or 8 or 9 or 10 or 11):
            return "discard"
    #in addition to the situations above,you may want to draw from stock
    return "stock"
    


def discard(hand, last_turn, picked_up_discard_cards, player_position, wildcard_rank, num_turns_this_round):
    """
    (list,bool,list,int,int,int) -> int
    
    Decides which card to discard from the player’s hand based on the wildcard for this turn,
    the possible arrangements for the player’s hand and next_player's picked_up_discard_card.
    Returns the card as an integer.
    
    >>> discard([1,2,3,15],False,[[5],[6],[7]],1,1,1)
    15
    >>> discard([1,2,3,15,31],False,[[5],[6],[7]],1,9,1)
    31
    >>> discard([1,2,3,15,31],False,[[5],[6],[7]],1,7,1)
    15
    """
    penalty_pts=100000
    penalty_points=[2,3,4,5,6,7,8,9,10,10,10,10,1]
    
    
    #first we want to check discard which card in our hand(after drawing)
    #can help us the fewest penalty points
    
    for i in range(len(hand)):
        #we create a new_hand each time
        new_hand=hand[:]
        #then remove one card each time from new_hand
        #we don't want to modify our hand
        new_hand.remove(new_hand[i])
        #find all arrangements after remove the card
        hand_arrangement=get_arrangement(tuple(new_hand),wildcard_rank)
        #remove all arrangements and calculate penalty points
        for arrangement in hand_arrangement:
            for j in range(len(arrangement)):
                new_hand.remove(arrangement[j])
        hand_penalty_pts=calculate_round_points(new_hand)
        
        
        #at first,we created a variable with extreme large penalty points
        #to make sure this conditional statment evaluates to True at least once
        #if remove a card can help us have fewer penalty points
        #then we want to discard this card
        if hand_penalty_pts<penalty_pts:
            penalty_pts=hand_penalty_pts
            discard_card=hand[i]
    #after finishing this for loop,
    #discard_card is the card which helps us have the fewest penalty points
    
    
    
    #The following code is about hindering the next player
    #if they keep drawing some cards with some same ranks
    #then we may not want to discard the card with these ranks
    #anyway,we should still guarantee ourselves don't have too large penalty points
    
    
    #firstly,find our player's position and the next player's position
    #if our player_position is not the last one,
    #next_player's position is one adding to our position
    if player_position<len(picked_up_discard_cards)-1:
        next_player_picked=picked_up_discard_cards[player_position+1]
    #if our player is the last one
    #then next_player's position should be the first one
    elif player_position==len(picked_up_discard_cards)-1:
        next_player_picked=picked_up_discard_cards[0]
    #now all the cards which next_player has drawn from top_discard so far
    #are stored in next_player_picked
    
    
    #if next player haven't draw any card from the discard pile yet,
    #then we cannot obtain any information from picked_up_discard_cards
    #so we simply discard the discard_card
    if next_player_picked==[]:
        return discard_card
    
    
    #then,we find the occurrence of different ranks
    occurrence=[]
    for i in range(len(next_player_picked)):
        #check for each card's rank and initialize num as 0
        checking_rank=get_rank(next_player_picked[i])
        num=0
        for j in range(len(next_player_picked)):
            #traverse all the cards again
            #we don't remove duplicates because we could have
            #same index for occurrence and next_player_picked
            if get_rank(next_player_picked[j])==checking_rank:
                num+=1
        occurrence.append(num)
    #we find the number of the max occurrence
    max_occurrence=max(occurrence)
    
    
    #then we find the indices of the cards which have the max_occurrence
    #we may have same occurrence for different ranks
    index=[]
    for i in range(len(occurrence)):
        if max_occurrence==occurrence[i]:
            index.append(i)
    
    
    #initialize the next_player_wanted_rank with the first rank
    next_player_wanted_rank=get_rank(next_player_picked[index[0]])
    #the occurrence of different ranks might be same
    all_possible_wanted_rank=[]
    all_possible_wanted_rank.append(next_player_wanted_rank)
    #if next_player want different ranks,add them all in all_possible_wanted_rank
    for element in index:
        #as we don't remove duplicates before
        #here we don't want same rank occurring more than once
        #so if the rank is already in all_possible_wanted_rank,we don't add it twice.
        if get_rank(next_player_picked[element]) not in all_possible_wanted_rank:
            all_possible_wanted_rank.append(get_rank(next_player_picked[element]))
    #so far, we have all_possible_wanted_rank storing all the ranks next_player keep picking          
    
    
    
    #if our discard_card's rank is not what the next player wants,
    #then we can discard this card
    if get_rank(discard_card) not in all_possible_wanted_rank:
        return discard_card
    #if the discard_card's rank is what the next_player wants,
    #but keeping this card will make us have too large penalty points
    #then still discard it,we don't want to hinder ourselves
    elif get_rank(discard_card)==(6 or 7 or 8 or 9 or 10 or 11):
        return discard_card
    
    #then we can try to hinder next_player
    #remove the discard_card and check for arrangements again
    #because we need to discard a new card which help us have the fewest penalty points
    hand.remove(discard_card)
    hand_arrangements=get_arrangement(tuple(hand),wildcard_rank)
    #then remove all the arrangements
    #because we don't want to discard a card in arrangements
    for arrangement in hand_arrangements:
        for card in arrangement:
            hand.remove(card)
    
    #then we have our hand with all the remaining cards
    #if we discard the discard_card and then we can going out
    #then just discard it even next player wants this card 
    if hand==[]:
        return discard_card
    
    
    #if we cannot going out at this moment
    else:
        new_discard=hand[0]
        #we want to check which card's rank is not what next_player wants
        for element in hand:
            if get_rank(element) in all_possible_wanted_rank:
                hand.remove(element)
        #if next player wants all our possible discard cards
        #we still discard discard_card because it helps us have the fewest penalty points
        if hand==[]:
            return discard_card
        else:
            #then if we have a rank occurring more than once
            #but cannot form an arrangement at this moment
            #we don't want to discard it because we almost have a group
            for element in hand:
                num_occurrence=hand.count(element)
                if num_occurrence>1:
                    hand.remove(element)
            #after removing all cards with rank occurring more than once
            #if we don't have any cards,return discard_card
            if hand==[]:
                return discard_card
            
            for element in hand:
                #then check for remaining cards' penalty points,
                #the variable is defined at top
                #we want to return new_discard which have largest penalty points
                if penalty_points[get_rank(element)]>penalty_points[get_rank(new_discard)]:
                    new_discard=element
            return new_discard
    #in case there are some cases we don't take into consideration
    #guarantee that we have a discard_card returned
    return discard_card
        
        
        
