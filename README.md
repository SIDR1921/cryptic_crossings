# 🔢 Cryptic Crossings

A unique puzzle game that combines **Cryptarithmetic** (alphametic) puzzles with the classic **Missionaries and Cannibals** river crossing problem. Solve mathematical word puzzles to unlock challenging logic-based river crossing scenarios!

## 🎮 Game Overview

Cryptic Crossings features two interconnected puzzle types:

1. **Cryptarithmetic Puzzles**: Decode mathematical equations where letters represent digits
2. **River Crossing Challenges**: Transport missionaries and cannibals across a river following specific safety rules

The twist? You must solve the cryptarithmetic puzzle first to unlock the river crossing challenge for each level!

## 🖼️ Screenshots

### Main Game Interface
- Left Panel: Cryptarithmetic puzzle with letter-to-digit input
- Right Panel: Interactive river crossing visualization with clickable characters

### Game Features
- 3 progressively challenging levels
- Beautiful GUI with Tkinter
- Sound effects (optional, requires pygame)
- Progress saving between sessions
- Visual feedback and error messages

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Required Dependencies
```bash
pip install -r requirements.txt
```

### Optional Dependencies (for sound effects)
```bash
pip install pygame numpy
```

## 🎯 How to Play

### 1. Cryptarithmetic Puzzles
- Each letter represents a unique digit (0-9)
- Leading letters cannot be zero
- Solve the equation: `WORD1 + WORD2 = RESULT`

### 2. River Crossing Rules
- **Safety Rule**: Cannibals cannot outnumber Missionaries on either side (unless no Missionaries present)
- **Boat Rule**: Boat must have at least 1 passenger to travel
- **Goal**: Transport everyone from Left Bank to Right Bank

### 3. Game Progression
1. Enter your solution for the cryptarithmetic puzzle
2. Click "Verify Solution" to unlock the river crossing
3. Click on characters to move them to/from the boat
4. Use "Row Boat" to cross the river
5. Complete the level to advance!

## 📚 Level Guide

### Level 1: SEND + MORE = MONEY
- **Solution**: S=9, E=5, N=6, D=7, M=1, O=0, R=8, Y=2
- **River Challenge**: 3 Missionaries, 3 Cannibals, Boat capacity 2

### Level 2: TWO + TWO = FOUR
- **Solution**: T=7, W=3, O=4, F=1, U=6, R=8
- **River Challenge**: 4 Missionaries, 4 Cannibals, Boat capacity 3

### Level 3: THIS + IS = GOOD
- **Solution**: T=1, H=9, I=5, S=3, G=2, O=0, D=6
- **River Challenge**: 5 Missionaries, 5 Cannibals, Boat capacity 3

## 🎮 Running the Game

1. **Clone or download** this repository
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Run the game**: `python cryptic_crossings.py`

Or if running from a Jupyter notebook:
```python
# Execute the game cell in the notebook
%run cryptic_crossings.ipynb
```

## 🎵 Sound Effects

The game includes optional sound effects that enhance the gaming experience:
- Success sounds when solving puzzles
- Failure sounds for incorrect solutions
- Movement sounds during river crossing

To enable sound effects, install the optional dependencies:
```bash
pip install pygame numpy
```

If these packages are not installed, the game will run silently without any issues.

## 🧩 Strategy Tips

### Cryptarithmetic
- Start with constraints (leading letters ≠ 0)
- Look for patterns and repeated letters
- Use logical deduction to narrow down possibilities

### River Crossing
- **Start with Cannibals**: Move cannibals first to avoid safety violations
- **Plan return trips**: Someone must bring the boat back
- **Use boat capacity**: Take advantage of the full capacity when possible
- **Monitor ratios**: Keep track of Missionary:Cannibal ratios on both sides

## 🔧 Technical Details

### Built With
- **Python 3.7+**: Core programming language
- **Tkinter**: GUI framework (included with Python)
- **Pygame** (optional): Sound effects
- **NumPy** (optional): Audio wave generation
- **JSON**: Progress saving

### File Structure
```
cryptic_crossings/
├── cryptic_crossings.py          # Main game file
├── cryptic_crossings.ipynb       # Jupyter notebook version
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── cryptic_crossings_progress.json  # Auto-generated save file
```

### Features
- **Auto-save**: Game progress is automatically saved locally
- **Input validation**: Real-time validation of cryptarithmetic solutions
- **Visual feedback**: Clear error messages and success indicators
- **Responsive UI**: Optimized layout with proper spacing and colors

## 🤝 Contributing

Contributions are welcome! Here are some ways you can help:

1. **Report bugs** or suggest features via GitHub Issues
2. **Add new levels** with different cryptarithmetic puzzles
3. **Improve UI/UX** with better graphics or animations
4. **Optimize performance** or add new features
5. **Write tests** to ensure game stability

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request with a clear description

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Inspired by classic mathematical and logical puzzles
- Cryptarithmetic puzzles are a well-known type of mathematical puzzle
- Missionaries and Cannibals is a traditional river-crossing puzzle
- Built as an educational tool for puzzle enthusiasts

## 📞 Support

If you encounter any issues or have questions:

1. Check the existing GitHub Issues
2. Create a new issue with detailed information
3. Include your Python version and operating system
4. Describe the steps to reproduce the problem

---

**Enjoy solving puzzles and happy crossing!** 🌉✨
