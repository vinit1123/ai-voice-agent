from memory import (
    search_memory
)
from memory import (
    save_memory,
    get_memories
)

save_memory(
    "My name is Vinit"
)

save_memory(
    "I work at Extramarks"
)

print(
    search_memory(
        "What is my name?"
    )
)