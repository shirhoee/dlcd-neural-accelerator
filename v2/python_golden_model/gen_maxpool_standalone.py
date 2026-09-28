import random

def relu(x): return x if x > 0 else 0

def hex16(val): return f"{(val & 0xFFFF):04x}"

def main():
    random.seed(42)
    
    # 4 frames (3 random + 1 edge cases), 4 channels, 20x20
    frames = []
    
    # Frame 0-2: Random
    for f in range(3):
        channels = []
        for ch in range(4):
            grid = [[random.randint(-32768, 32767) for _ in range(20)] for _ in range(20)]
            channels.append(grid)
        frames.append(channels)
        
    # Frame 3: Edge cases
    edge_channels = []
    for ch in range(4):
        grid = [[0 for _ in range(20)] for _ in range(20)]
        # Make first few windows specific test cases
        
        # Window 0: All negative (should output 0 after ReLU)
        grid[0][0], grid[0][1] = -5, -10
        grid[1][0], grid[1][1] = -3, -8
        
        # Window 1: 0x8000 (most negative)
        grid[0][2], grid[0][3] = -32768, -32768
        grid[1][2], grid[1][3] = -32768, -32768
        
        # Window 2: 0x7FFF (most positive)
        grid[0][4], grid[0][5] = 32767, 32767
        grid[1][4], grid[1][5] = 32767, 32767
        
        # Window 3: Ties
        grid[0][6], grid[0][7] = 50, 50
        grid[1][6], grid[1][7] = 50, -50
        
        # Window 4: Mixed signs
        grid[0][8], grid[0][9] = -10, 5
        grid[1][8], grid[1][9] = 10, -5
        
        edge_channels.append(grid)
    frames.append(edge_channels)
        
    # Write input hex -> 4 * 400 = 1600 lines
    in_lines = []
    for f in range(4):
        for r in range(20):
            for c in range(20):
                ch_vals = [frames[f][ch][r][c] for ch in range(4)]
                in_lines.append(" ".join(hex16(v) for v in ch_vals))
                
    with open('v2/python_golden_model/standalone_maxpool_in.txt', 'w') as fh:
        fh.write("\n".join(in_lines) + "\n")
        
    # Compute output expected -> 4 * 100 = 400 lines
    out_lines = []
    for f in range(4):
        for r in range(0, 20, 2):
            for c in range(0, 20, 2):
                ch_vals = []
                for ch in range(4):
                    w = [
                        frames[f][ch][r][c], frames[f][ch][r][c+1],
                        frames[f][ch][r+1][c], frames[f][ch][r+1][c+1]
                    ]
                    ch_vals.append(relu(max(w)))
                out_lines.append(" ".join(hex16(v) for v in ch_vals))
                
    with open('v2/python_golden_model/standalone_maxpool_out.txt', 'w') as fh:
        fh.write("\n".join(out_lines) + "\n")
        
    print("Standalone vectors generated with edge cases.")

if __name__ == '__main__':
    main()
