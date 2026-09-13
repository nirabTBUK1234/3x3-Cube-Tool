
import sys
import magiccube
from tqdm import tqdm


# ============================================================================
# KOCIEMBA FACELET ORDER
#
# 0-8   = U
# 9-17  = R
# 18-26 = F
# 27-35 = D
# 36-44 = L
# 45-53 = B
# ============================================================================

FACELET_NAMES = (
    # U
    "ULB", "UB", "URB",
    "UL",  "U",  "UR",
    "ULF", "UF", "URF",

    # R
    "URF", "UR", "URB",
    "FR",  "R",  "BR",
    "DRF", "DR", "DRB",

    # F
    "ULF", "UF", "URF",
    "LF",  "F",  "RF",
    "DLF", "DF", "DRF",

    # D
    "DLF", "DF", "DRF",
    "DL",  "D",  "DR",
    "DLB", "DB", "DRB",

    # L
    "ULB", "UL", "ULF",
    "BL",  "L",  "FL",
    "DLB", "DL", "DLF",

    # B
    "URB", "UB", "ULB",
    "BR",  "B",  "BL",
    "DRB", "DB", "DLB",
)


# ============================================================================
# CENTER POSITIONS
# ============================================================================

FACE_CENTER_INDEX = {
    "U": 4,
    "R": 13,
    "F": 22,
    "D": 31,
    "L": 40,
    "B": 49,
}


# ============================================================================
# COLORS
# ============================================================================

FACE_TO_COLOR = {
    "U": "White",
    "D": "Yellow",
    "F": "Green",
    "B": "Blue",
    "L": "Orange",
    "R": "Red",
}


# ============================================================================
# PIECE SLOTS
# ============================================================================

SLOT_INDICES = {}

for i, name in enumerate(FACELET_NAMES):
    SLOT_INDICES.setdefault(name, []).append(i)


# ============================================================================
# BUILD COLOR MAP
# ============================================================================

def build_color_map(solved_state):

    color_map = {}

    for face, index in FACE_CENTER_INDEX.items():

        raw_letter = solved_state[index]

        color_map[raw_letter] = FACE_TO_COLOR[face]

    return color_map


# ============================================================================
# GET COLORS OF A PIECE
# ============================================================================

def get_piece_colors(
    state,
    indices,
    color_map
):

    return [
        color_map.get(
            state[i],
            state[i]
        )
        for i in indices
    ]


# ============================================================================
# GET PIECE IDENTITY
#
# Order is ignored.
# This tells us which physical piece it is.
# ============================================================================

def piece_identity(
    state,
    indices,
    color_map
):

    return frozenset(
        color_map.get(
            state[i],
            state[i]
        )
        for i in indices
    )


# ============================================================================
# FIND EDGE MOVEMENTS + ORIENTATION
# ============================================================================

def find_edge_movements(
    before_state,
    after_state,
    color_map
):

    edge_slots = {
        slot: indices
        for slot, indices in SLOT_INDICES.items()
        if len(indices) == 2
    }

    before = {
        slot: get_piece_colors(
            before_state,
            indices,
            color_map
        )
        for slot, indices in edge_slots.items()
    }

    after = {
        slot: get_piece_colors(
            after_state,
            indices,
            color_map
        )
        for slot, indices in edge_slots.items()
    }

    movements = []

    used_targets = set()

    for from_slot, piece in before.items():

        piece_set = set(piece)

        for to_slot, target in after.items():

            if to_slot in used_targets:
                continue

            if set(target) != piece_set:
                continue

            if piece == target:
                orientation = "ORIENTED"
            else:
                orientation = "FLIPPED"

            movements.append(
                (
                    from_slot,
                    to_slot,
                    orientation,
                    piece
                )
            )

            used_targets.add(to_slot)

            break

    return movements


# ============================================================================
# FIND CORNER MOVEMENTS + ORIENTATION
# ============================================================================

def find_corner_movements(
    before_state,
    after_state,
    color_map
):

    corner_slots = {
        slot: indices
        for slot, indices in SLOT_INDICES.items()
        if len(indices) == 3
    }

    before = {
        slot: get_piece_colors(
            before_state,
            indices,
            color_map
        )
        for slot, indices in corner_slots.items()
    }

    after = {
        slot: get_piece_colors(
            after_state,
            indices,
            color_map
        )
        for slot, indices in corner_slots.items()
    }

    movements = []

    used_targets = set()

    for from_slot, piece in before.items():

        piece_set = set(piece)

        for to_slot, target in after.items():

            if to_slot in used_targets:
                continue

            if set(target) != piece_set:
                continue

            if piece == target:
                orientation = "ORIENTED"
            else:
                orientation = "TWISTED"

            movements.append(
                (
                    from_slot,
                    to_slot,
                    orientation,
                    piece
                )
            )

            used_targets.add(to_slot)

            break

    return movements


# ============================================================================
# CHECK IF ALL U-LAYER CORNERS ARE SOLVED
# ============================================================================

def corners_are_solved(
    before_state,
    after_state,
    color_map
):

    u_corners = [
        "ULB",
        "URB",
        "URF",
        "ULF",
    ]

    for slot in u_corners:

        indices = SLOT_INDICES[slot]

        before = get_piece_colors(
            before_state,
            indices,
            color_map
        )

        after = get_piece_colors(
            after_state,
            indices,
            color_map
        )

        if before != after:
            return False

    return True


# ============================================================================
# CHECK IF THIS IS AN ELL CASE
# ============================================================================

def is_ell_case(
    before_state,
    after_state,
    color_map
):

    return corners_are_solved(
        before_state,
        after_state,
        color_map
    )


# ============================================================================
# WRITE EDGE REPORT
# ============================================================================

def write_edge_report(
    out_f,
    before_state,
    after_state,
    color_map
):

    movements = find_edge_movements(
        before_state,
        after_state,
        color_map
    )

    for (
        from_slot,
        to_slot,
        orientation,
        colors
    ) in movements:

        if (
            from_slot == to_slot
            and orientation == "ORIENTED"
        ):
            continue

        color_text = "/".join(colors)

        out_f.write(
            f"    {from_slot} -> {to_slot}"
            f"  ({color_text})"
            f"  [{orientation}]\n"
        )


# ============================================================================
# WRITE CORNER REPORT
# ============================================================================

def write_corner_report(
    out_f,
    before_state,
    after_state,
    color_map
):

    movements = find_corner_movements(
        before_state,
        after_state,
        color_map
    )

    for (
        from_slot,
        to_slot,
        orientation,
        colors
    ) in movements:

        if (
            from_slot == to_slot
            and orientation == "ORIENTED"
        ):
            continue

        color_text = "/".join(colors)

        out_f.write(
            f"    {from_slot} -> {to_slot}"
            f"  ({color_text})"
            f"  [{orientation}]\n"
        )


# ============================================================================
# CONVERT LOWERCASE MOVES TO WIDE MOVES
#
# r  -> Rw
# r' -> Rw'
# r2 -> Rw2
#
# Same for l, u, d, f, b.
# ============================================================================

def convert_wide_moves(moves):

    table = {
        "r":  "Rw",
        "r'": "Rw'",
        "r2": "Rw2",

        "l":  "Lw",
        "l'": "Lw'",
        "l2": "Lw2",

        "u":  "Uw",
        "u'": "Uw'",
        "u2": "Uw2",

        "d":  "Dw",
        "d'": "Dw'",
        "d2": "Dw2",

        "f":  "Fw",
        "f'": "Fw'",
        "f2": "Fw2",

        "b":  "Bw",
        "b'": "Bw'",
        "b2": "Bw2",
    }
    result = []

    for move in moves.split():
        result.append(
        table.get(move, move)
        )

    return " ".join(result)

# ============================================================================
# PROCESS FILE
# ============================================================================

def process_cube_file(
    input_file_path,
    output_file_path
):

    # ------------------------------------------------------------------------
    # READ INPUT
    # ------------------------------------------------------------------------

    try:

        with open(
            input_file_path,
            "r"
        ) as f:

            lines = [
                line.strip()
                for line in f
                if line.strip()
            ]

    except FileNotFoundError:

        print(
            f"Error: input file "
            f"'{input_file_path}' not found."
        )

        return


    # ------------------------------------------------------------------------
    # CREATE SOLVED REFERENCE CUBE
    # ------------------------------------------------------------------------

    reference_cube = magiccube.Cube(3)

    reference_state = (
        reference_cube
        .get_kociemba_facelet_colors()
    )

    color_map = build_color_map(
        reference_state
    )

    del reference_cube


    # ------------------------------------------------------------------------
    # OPEN OUTPUT
    # ------------------------------------------------------------------------

    with open(
        output_file_path,
        "w"
    ) as out_f:

        out_f.write(
            "Orientation: "
            "White on top (U), "
            "Green facing front (F)\n"
        )

        out_f.write(
            "Color legend: "
            "U=White  "
            "D=Yellow  "
            "F=Green  "
            "B=Blue  "
            "L=Orange  "
            "R=Red\n"
        )

        out_f.write(
            "Position codes: "
            "U/R/F/D/L/B = centers, "
            "2 letters = edges, "
            "3 letters = corners\n"
        )

        out_f.write(
            "=" * 60
            + "\n\n"
        )


        # --------------------------------------------------------------------
        # PROCESS EVERY ALGORITHM
        # --------------------------------------------------------------------

        for line in tqdm(
            lines,
            desc="Processing algorithms",
            unit="alg"
        ):

            if ":" not in line:
                continue


            # ---------------------------------------------------------------
            # SPLIT NAME AND ALGORITHM
            # ---------------------------------------------------------------

            name, raw_moves = line.split(
                ":",
                1
            )

            name = name.strip()

            moves = (
                raw_moves
                .strip()
                .replace("`", "'")
            )


            # ---------------------------------------------------------------
            # CONVERT LOWERCASE MOVES
            # ---------------------------------------------------------------

            moves = convert_wide_moves(
                moves
            )


            # ---------------------------------------------------------------
            # WRITE NAME
            # ---------------------------------------------------------------

            out_f.write(
                f"{name}:\n"
            )


            cube = None


            try:

                # -----------------------------------------------------------
                # NEW SOLVED CUBE
                # -----------------------------------------------------------

                cube = magiccube.Cube(3)

                before_state = (
                    cube
                    .get_kociemba_facelet_colors()
                )


                # -----------------------------------------------------------
                # APPLY ALGORITHM
                # -----------------------------------------------------------

                cube.rotate(
                    moves
                )


                # -----------------------------------------------------------
                # GET RESULT
                # -----------------------------------------------------------

                after_state = (
                    cube
                    .get_kociemba_facelet_colors()
                )


                # -----------------------------------------------------------
                # CHECK ELL
                # -----------------------------------------------------------

                ell = is_ell_case(
                    before_state,
                    after_state,
                    color_map
                )


                if ell:

                    out_f.write(
                        "    ELL CASE: YES\n"
                    )

                else:

                    out_f.write(
                        "    ELL CASE: NO\n"
                    )


                # -----------------------------------------------------------
                # CORNERS
                # -----------------------------------------------------------

                out_f.write(
                    "    Corners:\n"
                )

                write_corner_report(
                    out_f,
                    before_state,
                    after_state,
                    color_map
                )


                # -----------------------------------------------------------
                # EDGES
                # -----------------------------------------------------------

                out_f.write(
                    "    Edges:\n"
                )

                write_edge_report(
                    out_f,
                    before_state,
                    after_state,
                    color_map
                )


            except Exception as e:

                out_f.write(
                    f"    ERROR: {e}\n"
                )


            out_f.write(
                "\n"
            )


            if cube is not None:
                del cube


    # ------------------------------------------------------------------------
    # DONE
    # ------------------------------------------------------------------------

    print()

    print(
        "Done."
    )

    print(
        f"Results written to "
        f"'{output_file_path}'"
    )


# ============================================================================
# MAIN
# ============================================================================

def Main():

    print(
        "=== ELL Cube Analyzer ==="
    )

    print()


    # ------------------------------------------------------------------------
    # INPUT FILE
    # ------------------------------------------------------------------------

    input_file = input(
        "Enter the path to your "
        "input .txt file: "
    ).strip()


    # Remove quotes if file was dragged
    # into the terminal.

    input_file = (
        input_file
        .strip('"')
        .strip("'")
    )


    if not input_file.lower().endswith(
        ".txt"
    ):

        print(
            "Error: Please provide "
            "a .txt file."
        )

        sys.exit(1)


    # ------------------------------------------------------------------------
    # OUTPUT FILE
    # ------------------------------------------------------------------------

    output_file = input(
        "Enter the path for the "
        "output .txt file "
        "(press Enter for "
        "'output_ell.txt'): "
    ).strip()


    output_file = (
        output_file
        .strip('"')
        .strip("'")
    )


    if not output_file:

        output_file = "output_ell.txt"


    # ------------------------------------------------------------------------
    # RUN
    # ------------------------------------------------------------------------

    process_cube_file(
        input_file,
        output_file
    )
if __name__ == "__main__":
    Main()

