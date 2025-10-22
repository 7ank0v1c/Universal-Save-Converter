# core/swap_utils.py

def byteswap(data: bytes, swap_size: int) -> bytes:
    """Swap the byte order of data in chunks of the given size."""
    if swap_size <= 1:
        return data

    swapped = bytearray(len(data))
    for i in range(0, len(data), swap_size):
        chunk = data[i:i + swap_size]
        swapped[i:i + len(chunk)] = chunk[::-1]
    return bytes(swapped)

def determine_swap_size(swap_required_from_table: bool = False, user_choice: str = "Default") -> int:
    """
    Determine the number of bytes to swap for endian conversion.
    
    Parameters:
        swap_required_from_table: Whether the conversion table suggests a swap.
        user_choice: User override ("Default", "2 bytes", "4 bytes").
        
    Returns:
        int: Number of bytes to swap (1, 2, or 4).
    """
    if user_choice == "2 bytes":
        return 2
    elif user_choice == "4 bytes":
        return 4
    else:  # Default
        return 2 if swap_required_from_table else 1
