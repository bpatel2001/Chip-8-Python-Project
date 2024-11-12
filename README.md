## Python Chip-8 Emulator

This is my project delving into interpreting and executing Chip-8 instructions, complete with input, sound and graphics handling using pygame.
![]([https://github.com/bpatel2001/Chip-8-Python-Project/blob/main/chipgif.gif])
## Requirements
- Python 3.x
- pygame

## Setup Instructions
1. **Clone repository**
```bash
  git clone https://github.com/bpatel2001/Chip-8-Python-Project.git
  cd Chip-8-Python-Project
```
2.  **Install dependencies**
```bash
  pip install pygame
```
3. **Run emulator**
```bash
  python chip8.py
```

## Key Mapping
The original CHIP-8 keypad uses a 4x4 hexadecimal layout. Here is the mapping being emulated on a keyboard:
``` 
  1 2 3 C           1 2 3 4
  4 5 6 D           Q W E R
  7 8 9 E     ->    A S D F
  A 0 B F           Z X C V
  Chip-8            Keyboard
```

## Issues
Currently unable to pass all of Timendus's quirk tests, which causes issues in some games. I plan to make more quirks be a toggle depending on the program.
![image](https://github.com/user-attachments/assets/b2305222-7169-420a-afb7-5200a86f3614)


## Acknowledgements
- [Tobias V. Langhoff's high level guide](https://tobiasvl.github.io/blog/write-a-chip-8-emulator/)
- [Cowgod's Technical Reference](http://devernay.free.fr/hacks/chip8/C8TECH10.HTM)
- [Timendus's Chip-8 Test Suite](https://github.com/Timendus/chip8-test-suite?tab=readme-ov-file#corax-opcode-test)
