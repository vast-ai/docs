import argparse
import os
import sys
import torch
import torch.distributed as dist
import torch.multiprocessing as mp
from datetime import timedelta

# 10s was too tight on multi-GPU hosts: with device_id= the rendezvous and
# broadcastUniqueNCCLID happen eagerly inside init_process_group, racing
# rank 0's TCPStore startup. PyTorch's own default is 30 minutes; 120s
# gives plenty of headroom for an 8-GPU init while still failing fast on
# a genuinely broken host.
DEFAULT_TIMEOUT = timedelta(seconds=120)

def func(args):
    """Example function to run on each rank. Prints a random tensor."""
    print(f"  Inside main_func, random tensor: {torch.randn(1)}")

def run(main_func, backend, num_machines, num_gpus, machine_rank, dist_url, args=()):
    """Spawns multiple workers (one per GPU) and runs 'distributed_worker' in each."""
    world_size = num_machines * num_gpus
    mp.spawn(
        distributed_worker,
        nprocs=num_gpus,
        args=(main_func, backend, world_size, num_gpus, machine_rank, dist_url, args),
        daemon=False,
    )

def distributed_worker(
    local_rank,
    main_func,
    backend,
    world_size,
    num_gpus_per_machine,
    machine_rank,
    dist_url,
    args,
    timeout=DEFAULT_TIMEOUT,
):
    """Entry point for each spawned process (each GPU)."""
    LOCAL_PROCESS_GROUP = None

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available. Please check your installation.")

    global_rank = machine_rank * num_gpus_per_machine + local_rank
    try:
        # Check GPU device bounds before we bind to one.
        if num_gpus_per_machine > torch.cuda.device_count():
            raise RuntimeError(
                f"[Rank {global_rank}] Not enough GPUs! Requested {num_gpus_per_machine}, found {torch.cuda.device_count()}."
            )

        # Bind this worker to its GPU before init so NCCL can use device_id
        # and avoid the "Guessing device ID based on global rank" warning.
        torch.cuda.set_device(local_rank)
        print(f"[Rank {global_rank}] Using GPU device {local_rank}.")

        # Initialize the default process group
        dist.init_process_group(
            backend=backend,
            init_method=dist_url,
            world_size=world_size,
            rank=global_rank,
            timeout=timeout,
            device_id=torch.device(f"cuda:{local_rank}"),
        )
        print(f"[Rank {global_rank}] init_process_group succeeded.")

        # Synchronize all ranks
        dist.barrier()
        print(f"[Rank {global_rank}] Barrier reached. GPUs synchronized.")

        # Optionally create a local process group containing only ranks on this node
        num_machines = world_size // num_gpus_per_machine
        for idx in range(num_machines):
            ranks_on_machine = list(range(idx * num_gpus_per_machine, (idx + 1) * num_gpus_per_machine))
            pg = dist.new_group(ranks_on_machine)
            if idx == machine_rank:
                LOCAL_PROCESS_GROUP = pg

        # Run the user function
        print(f"[Rank {global_rank}] Running main_func() ...")
        main_func(args)
        print(f"[Rank {global_rank}] main_func() complete. Success.")

    except Exception as e:
        print(f"[Rank {global_rank}] ERROR: {e}")
        raise
    finally:
        # Cleanly destroy the process group to avoid 'process group has NOT been destroyed' warning
        if dist.is_initialized():
            dist.destroy_process_group()
            print(f"[Rank {global_rank}] Process group destroyed. Goodbye!")

def main():
    """Parses arguments, then calls 'run'."""
    torch.set_num_threads(1)
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["NCCL_DEBUG"] = "INFO"

    print("=== Starting NCCL test script ===")
    print(f"PyTorch CUDA version: {torch.version.cuda}")
    print(f"cuDNN version: {torch.backends.cudnn.version()}")
    nccl_version = torch.cuda.nccl.version() if hasattr(torch.cuda.nccl, 'version') else "UNKNOWN"
    print(f"NCCL version: {nccl_version}\n")

    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", type=str, default="NCCL", help="'gloo' or 'NCCL'.")
    parser.add_argument("--num-gpus", type=int, default=1, help="# GPUs per machine.")
    parser.add_argument("--num-machines", type=int, default=1, help="# of machines.")
    parser.add_argument(
        "--machine-rank",
        type=int,
        default=0,
        help="the rank of this machine (unique per machine).",
    )
    parser.add_argument(
        "--dist-url",
        type=str,
        default="tcp://127.0.0.1:1234",
        help="Initialization URL for PyTorch distributed backend.",
    )

    args = parser.parse_args()

    # Print out a quick summary
    print(f"Requested backend: {args.backend}")
    print(f"num_gpus per machine: {args.num_gpus}")
    print(f"num_machines: {args.num_machines}")
    print(f"machine_rank: {args.machine_rank}")
    print(f"dist_url: {args.dist_url}")
    print("")

    try:
        run(
            main_func=func,
            backend=args.backend,
            num_machines=args.num_machines,
            num_gpus=args.num_gpus,
            machine_rank=args.machine_rank,
            dist_url=args.dist_url,
            args=()
        )
        print("=== NCCL test completed SUCCESSFULLY. ===")
    except Exception as e:
        print(f"=== NCCL test FAILED with error: {e} ===")
        sys.exit(1)


if __name__ == '__main__':
    main()
