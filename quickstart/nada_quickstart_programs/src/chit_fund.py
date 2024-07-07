from nada_dsl import *

def nada_main():
    num_participants = 3  # Define the number of participants
    
    # 1. Parties initialization
    parties = [Party(name=f"Party{i}") for i in range(num_participants)]
    outparty = Party(name="OutParty")
    
    # 2. Inputs initialization
    bids = [SecretUnsignedInteger(Input(name=f"bid_p{i}", party=parties[i])) for i in range(num_participants)]
    current_month = PublicInteger(Input(name="current_month", party=outparty))
    bid_winners = [PublicInteger(Input(name=f"bid_winner_{i}", party=outparty)) for i in range(num_participants)]
    # current_month = -1
    # bid_winners = [-1, -1, -1]

    # 3. Computation
    # Find the lowest bid and the corresponding party
    min_bid = bids[0]
    min_bidder = Integer(0)
    
    for i in range(1, num_participants):
        is_lower = bids[i] < min_bid
        min_bid = is_lower.if_else(bids[i], min_bid)
        min_bidder = is_lower.if_else(Integer(i), min_bidder)
    
    # Calculate the contribution amount
    contribution_amount = min_bid / UnsignedInteger(num_participants)
    
    # 4. Outputs
    bid_winner_output = Output(min_bidder, name="bid_winner", party=outparty)
    contribution_amount_output = Output(contribution_amount, name="contribution_amount", party=outparty)
    
    return [bid_winner_output, contribution_amount_output]
