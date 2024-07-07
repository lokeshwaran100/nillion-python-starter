import asyncio
import os
from nada_dsl.nada_types.types import PublicInteger
import py_nillion_client as nillion

from py_nillion_client import NodeKey, UserKey
from dotenv import load_dotenv

from cosmpy.aerial.client import LedgerClient
from cosmpy.aerial.wallet import LocalWallet
from cosmpy.crypto.keypairs import PrivateKey

from nillion_python_helpers import get_quote_and_pay, create_nillion_client, create_payments_config

home = os.getenv("HOME")
load_dotenv(f"{home}/.config/nillion/nillion-devnet.env")

async def main():
    cluster_id = os.getenv("NILLION_CLUSTER_ID")
    grpc_endpoint = os.getenv("NILLION_NILCHAIN_GRPC")
    chain_id = os.getenv("NILLION_NILCHAIN_CHAIN_ID")

    num_participants = 3
    current_month = 1  # Example current month, you can change this as needed
    previous_bid_winners = [0] * current_month  # Example list of previous bid winners

    # 1. Initialize the general client
    seed = "my_seed"
    userkey = UserKey.from_seed(seed)
    nodekey = NodeKey.from_seed(seed)
    general_client = create_nillion_client(userkey, nodekey)
    general_payments_config = create_payments_config(chain_id, grpc_endpoint)
    general_payments_client = LedgerClient(general_payments_config)
    general_payments_wallet = LocalWallet(
        PrivateKey(bytes.fromhex(os.getenv("NILLION_NILCHAIN_PRIVATE_KEY_0"))),
        prefix="nillion",
    )

    # 2. Store the program
    program_name = "chit_fund"
    program_mir_path = f"../nada_quickstart_programs/target/{program_name}.nada.bin"
    if not os.path.exists(program_mir_path):
        raise FileNotFoundError(
            f"The file '{program_mir_path}' does not exist. Ensure you compiled the PyNada programs."
        )

    print(f"Storing program in the network: {program_name}")
    receipt_store_program = await get_quote_and_pay(
        general_client,
        nillion.Operation.store_program(program_mir_path),
        general_payments_wallet,
        general_payments_client,
        cluster_id,
    )

    action_id = await general_client.store_program(
        cluster_id, program_name, program_mir_path, receipt_store_program
    )
    program_id = general_client.user_id + "/" + program_name
    print(f"Program ID: {program_id}")

    # 3. Store the inputs
    bids = [100, 200, 150]  # Example bids for the participants
    bid_winners = previous_bid_winners.copy()
    
    # inputs = {
    #     "current_month": nillion.Integer(current_month),
    #     **{f"bid_winner_{i}": nillion.Integer(-1) for i in range(num_participants)},
    # }
    
    inputs = {
        "current_month": nillion.Integer(current_month),
        "bid_winner_0": nillion.Integer(-1),
        "bid_winner_1": nillion.Integer(-1),
        "bid_winner_2": nillion.Integer(-1),
        "bid_p0": nillion.SecretUnsignedInteger(100),
        "bid_p1": nillion.SecretUnsignedInteger(200),
        "bid_p2": nillion.SecretUnsignedInteger(150),
    }

    # print(inputs)

    input_values = nillion.NadaValues(inputs)
    print(input_values)
    
    # store_ids = []
    # for p in range(num_participants):
    #     party_p = general_client
    #     print("party_p: ", party_p)
    #     p_bid_dic = {}
    #     p_bid = nillion.SecretUnsignedInteger(bids[p])
    #     p_bid_dic["bid_p" + str(p)] = p_bid
    #     p_to_be_store_values = nillion.NadaValues(p_bid_dic)

    #     p_permissions = nillion.Permissions.default_for_user(party_p.user_id)
    #     p_permissions.add_compute_permissions(
    #         {
    #             general_client.user_id: {program_id},
    #         }
    #     )

    #     receipt_store = await get_quote_and_pay(
    #         party_p,
    #         nillion.Operation.store_values(p_to_be_store_values, ttl_days=5),
    #         general_payments_wallet,
    #         general_payments_client,
    #         cluster_id,
    #     )

    #     print("Storing bid by party " + str(p) + f": {p_to_be_store_values}")
    #     store_id = await party_p.store_values(
    #         cluster_id, p_to_be_store_values, p_permissions, receipt_store
    #     )
    #     store_ids.append(store_id)
    #     print(f"Stored bid by party " + str(p) + f" with store_id ={store_id}")

    # for p in range(num_participants):
    #     party_p = general_client
    #     print("bid_winner_: ", party_p)
    #     p_bid_dic = {}
    #     p_bid_dic["bid_winner_" + str(p)] = nillion.Integer(-1)
    #     p_to_be_store_values = nillion.NadaValues(p_bid_dic)

    #     p_permissions = nillion.Permissions.default_for_user(party_p.user_id)
    #     p_permissions.add_compute_permissions(
    #         {
    #             general_client.user_id: {program_id},
    #         }
    #     )

    #     receipt_store = await get_quote_and_pay(
    #         party_p,
    #         nillion.Operation.store_values(p_to_be_store_values, ttl_days=5),
    #         general_payments_wallet,
    #         general_payments_client,
    #         cluster_id,
    #     )

    #     print("Storing bid winner " + str(p) + f": {p_to_be_store_values}")
    #     store_id = await party_p.store_values(
    #         cluster_id, p_to_be_store_values, p_permissions, receipt_store
    #     )
    #     store_ids.append(store_id)
    #     print(f"Stored bid winner " + str(p) + f" with store_id ={store_id}")

    # p_bid = nillion.Integer(-1)
    # p_bid_dic["current_month"] = p_bid
    # p_to_be_store_values = nillion.NadaValues(p_bid_dic)

    # p_permissions = nillion.Permissions.default_for_user(party_p.user_id)
    # p_permissions.add_compute_permissions(
    #     {
    #         general_client.user_id: {program_id},
    #     }
    # )

    # receipt_store = await get_quote_and_pay(
    #     party_p,
    #     nillion.Operation.store_values(p_to_be_store_values, ttl_days=5),
    #     general_payments_wallet,
    #     general_payments_client,
    #     cluster_id,
    # )

    # print("Storing current month " + f": {p_to_be_store_values}")
    # store_id = await party_p.store_values(
    #     cluster_id, p_to_be_store_values, p_permissions, receipt_store
    # )
    # store_ids.append(store_id)
    # print(f"Stored current month " + f" with store_id ={store_id}")

    # Set permissions
    permissions = nillion.Permissions.default_for_user(general_client.user_id)
    permissions.add_compute_permissions({general_client.user_id: {program_id}})

    receipt_store = await get_quote_and_pay(
        general_client,
        nillion.Operation.store_values(input_values, ttl_days=5),
        general_payments_wallet,
        general_payments_client,
        cluster_id,
    )

    store_id = await general_client.store_values(
        cluster_id, input_values, permissions, receipt_store
    )

    # 4. Bind parties
    bindings = nillion.ProgramBindings(program_id)
    for i in range(num_participants):
        bindings.add_input_party(f"Party{i}", general_client.party_id)
    bindings.add_output_party("OutParty", general_client.party_id)

    # 5. Compute
    receipt_compute = await get_quote_and_pay(
        general_client,
        nillion.Operation.compute(program_id, nillion.NadaValues({})),
        general_payments_wallet,
        general_payments_client,
        cluster_id,
    )

    compute_id = await general_client.compute(
        cluster_id, bindings, [store_id], nillion.NadaValues({}), receipt_compute
    )

    print(f"Computation sent to the network, compute_id: {compute_id}")
    print("Waiting for computation response...")

    while True:
        compute_event = await general_client.next_compute_event()
        if isinstance(compute_event, nillion.ComputeFinishedEvent):
            print(f"Compute complete for compute_id {compute_event.uuid}")
            dict_result = compute_event.result.value
            print(f"The result is: {dict_result}\n")
            
            # Update the bid winners list with the new winner
            new_winner = dict_result["bid_winner"]
            bid_winners.append(new_winner)

            # Print the updated bid winners list
            print(f"Updated bid winners list: {bid_winners}")
            break

if __name__ == "__main__":
    asyncio.run(main())