def cast_ray(start_pos, vector, snake_body, grid_size=100):
        """
        Casts a ray in a specific vector direction (dx, dy) and returns distance to collision.
        Handles diagonal vectors like (1, 1) or (-1, 1).
        """
        head_x, head_y = start_pos
        vx, vy = vector
        
        # We limit the ray to a reasonable max distance to save CPU 
        # (e.g., half the grid is usually enough to know it's "Open Ocean")
        max_dist = grid_size // 2 
        
        for dist in range(1, max_dist + 1):
            # Calculate next cell
            next_x = (head_x + vx * dist) % grid_size
            next_y = (head_y + vy * dist) % grid_size
            
            # Check collision with body
            # Note: We slice snake_body[1:] to ignore the head itself
            if (next_x, next_y) in snake_body[1:]:
                return dist
                
        return max_dist

def get_space_density(snake, current_dir, grid_size=100):
    """
    Calculates the 'Space Advantage' (-1 to 1).
    -1.0 = Left is Open, Right is Cramped.
    +1.0 = Right is Open, Left is Cramped.
    """
    head = snake[0]
    dx, dy = current_dir # Current movement vector (e.g., 1, 0)
    # --- DEFINE VECTORS ---
    # We derive relative vectors using linear algebra rotation
    
    # Left Side Vectors
    vec_left      = (dy, -dx)            # -90 degrees
    vec_fwd_left  = (dx + dy, dy - dx)   # -45 degrees
    vec_back_left = (-dx + dy, -dy - dx) # -135 degrees
    
    # Right Side Vectors
    vec_right      = (-dy, dx)           # +90 degrees
    vec_fwd_right  = (dx - dy, dy + dx)  # +45 degrees
    vec_back_right = (-dx - dy, -dy + dx)# +135 degrees
    # --- CAST RAYS ---
    # Sum the distances to get a "Volume" score
    left_score = (
        cast_ray(head, vec_left, snake, grid_size) +
        cast_ray(head, vec_fwd_left, snake, grid_size) +
        cast_ray(head, vec_back_left, snake, grid_size)
    )
    
    right_score = (
        cast_ray(head, vec_right, snake, grid_size) +
        cast_ray(head, vec_fwd_right, snake, grid_size) +
        cast_ray(head, vec_back_right, snake, grid_size)
    )
    
    # --- NORMALIZE ---
    # Max possible score is (3 rays * max_dist)
    sensitivity = 50
    
    # Calculate Delta: (Right - Left) / Max
    # If Right is huge (300) and Left is tiny (10), result is +0.9 (Go Right)
    raw_val = (right_score - left_score) / sensitivity
    
    # Clamp between -1 and 1
    return max(-1.0, min(1.0, raw_val))