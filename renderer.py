
import sys
import glfw

from OpenGL.GL import *
from OpenGL.GLU import *

import magiccube

from cubeTool import convert_wide_moves


# ============================================================================
# SETTINGS
# ============================================================================

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 800

CUBIE_SIZE = 1.0

ROTATION_SPEED = 0.35
KEY_ROTATION = 8.0


# ============================================================================
# COLORS
# ============================================================================

COLORS = {
    "white":  (1.0, 1.0, 1.0),
    "yellow": (1.0, 0.85, 0.0),
    "green":  (0.0, 0.65, 0.15),
    "blue":   (0.05, 0.25, 1.0),
    "orange": (1.0, 0.35, 0.0),
    "red":    (0.9, 0.05, 0.05),
    "black":  (0.03, 0.03, 0.03),
}


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

FACE_START = {
    "U": 0,
    "R": 9,
    "F": 18,
    "D": 27,
    "L": 36,
    "B": 45,
}


# ============================================================================
# CENTER POSITIONS
# ============================================================================

CENTER_INDEX = {
    "U": 4,
    "R": 13,
    "F": 22,
    "D": 31,
    "L": 40,
    "B": 49,
}


# ============================================================================
# FACE COLORS
# ============================================================================

FACE_COLORS = {
    "U": "white",
    "D": "yellow",
    "F": "green",
    "B": "blue",
    "L": "orange",
    "R": "red",
}


# ============================================================================
# BUILD COLOR MAP
# ============================================================================

def build_color_map():

    cube = magiccube.Cube(3)

    state = (
        cube
        .get_kociemba_facelet_colors()
    )

    color_map = {}

    for face, index in CENTER_INDEX.items():

        raw_color = state[index]

        color_map[raw_color] = FACE_COLORS[face]

    return color_map


# ============================================================================
# GET CUBE STATE
# ============================================================================

def get_cube_state(moves=""):

    cube = magiccube.Cube(3)

    if moves:

        moves = convert_wide_moves(
            moves
        )

        cube.rotate(
            moves
        )

    return (
        cube
        .get_kociemba_facelet_colors()
    )


# ============================================================================
# CUBE RENDERER
# ============================================================================

class CubeRenderer:

    def __init__(self):

        # ---------------------------------------------------------------
        # CUBE
        # ---------------------------------------------------------------

        self.color_map = (
            build_color_map()
        )

        self.state = (
            get_cube_state()
        )


        # ---------------------------------------------------------------
        # ALGORITHMS
        # ---------------------------------------------------------------

        self.algorithms = []

        self.current_index = 0

        self.current_algorithm = (
            "No algorithm loaded"
        )


        # ---------------------------------------------------------------
        # CAMERA
        # ---------------------------------------------------------------

        self.camera_distance = 9.0

        self.camera_x = 25.0

        self.camera_y = -35.0


        # ---------------------------------------------------------------
        # MOUSE
        # ---------------------------------------------------------------

        self.dragging = False

        self.last_mouse_x = 0

        self.last_mouse_y = 0


# ============================================================================
# LOAD FILE
# ============================================================================

    def load_file(
        self,
        filename
    ):

        self.algorithms = []

        try:

            with open(
                filename,
                "r"
            ) as f:

                for line in f:

                    line = line.strip()

                    if not line:
                        continue

                    if ":" not in line:
                        continue

                    name, moves = (
                        line.split(
                            ":",
                            1
                        )
                    )

                    name = name.strip()

                    moves = (
                        moves
                        .strip()
                        .replace("`", "'")
                    )

                    self.algorithms.append(
                        (
                            name,
                            moves
                        )
                    )

        except Exception as e:

            print(
                f"Error loading file: {e}"
            )

            return


        if not self.algorithms:

            print(
                "No algorithms found."
            )

            return


        self.current_index = 0

        self.show_algorithm()


# ============================================================================
# SHOW CURRENT ALGORITHM
# ============================================================================

    def show_algorithm(self):

        if not self.algorithms:
            return


        name, moves = (
            self.algorithms[
                self.current_index
            ]
        )


        self.current_algorithm = (
            f"{name}: {moves}"
        )


        try:

            self.state = (
                get_cube_state(
                    moves
                )
            )

        except Exception as e:

            print(
                f"Error applying algorithm:"
            )

            print(
                f"  {moves}"
            )

            print(
                f"  {e}"
            )

            return


        print(
            f"[{self.current_index + 1}/"
            f"{len(self.algorithms)}] "
            f"{self.current_algorithm}"
        )


# ============================================================================
# NEXT ALGORITHM
# ============================================================================

    def next_algorithm(self):

        if not self.algorithms:
            return


        self.current_index += 1


        if (
            self.current_index
            >= len(self.algorithms)
        ):

            self.current_index = 0


        self.show_algorithm()


# ============================================================================
# PREVIOUS ALGORITHM
# ============================================================================

    def previous_algorithm(self):

        if not self.algorithms:
            return


        self.current_index -= 1


        if self.current_index < 0:

            self.current_index = (
                len(self.algorithms) - 1
            )


        self.show_algorithm()


# ============================================================================
# GET STICKER COLOR
# ============================================================================

    def get_sticker_color(
        self,
        face,
        row,
        col
    ):

        start = FACE_START[face]

        index = (
            start
            + row * 3
            + col
        )


        raw_color = self.state[index]


        color_name = (
            self.color_map.get(
                raw_color,
                "black"
            )
        )


        return COLORS[color_name]


# ============================================================================
# DRAW QUAD
# ============================================================================

    def draw_quad(
        self,
        color,
        vertices
    ):

        glColor3f(
            color[0],
            color[1],
            color[2]
        )


        glBegin(
            GL_QUADS
        )


        for vertex in vertices:

            glVertex3f(
                vertex[0],
                vertex[1],
                vertex[2]
            )


        glEnd()


# ============================================================================
# DRAW CUBIE
# ============================================================================

    def draw_cubie(
        self,
        x,
        y,
        z,
        stickers
    ):

        half = (
            CUBIE_SIZE / 2
        )


        x1 = x - half
        x2 = x + half

        y1 = y - half
        y2 = y + half

        z1 = z - half
        z2 = z + half


        black = COLORS["black"]


        # ----------------------------------------------------------------
        # FRONT
        # ----------------------------------------------------------------

        self.draw_quad(
            black,
            [
                (x1, y1, z2),
                (x2, y1, z2),
                (x2, y2, z2),
                (x1, y2, z2),
            ]
        )


        # ----------------------------------------------------------------
        # BACK
        # ----------------------------------------------------------------

        self.draw_quad(
            black,
            [
                (x2, y1, z1),
                (x1, y1, z1),
                (x1, y2, z1),
                (x2, y2, z1),
            ]
        )


        # ----------------------------------------------------------------
        # RIGHT
        # ----------------------------------------------------------------

        self.draw_quad(
            black,
            [
                (x2, y1, z2),
                (x2, y1, z1),
                (x2, y2, z1),
                (x2, y2, z2),
            ]
        )


        # ----------------------------------------------------------------
        # LEFT
        # ----------------------------------------------------------------

        self.draw_quad(
            black,
            [
                (x1, y1, z1),
                (x1, y1, z2),
                (x1, y2, z2),
                (x1, y2, z1),
            ]
        )


        # ----------------------------------------------------------------
        # TOP
        # ----------------------------------------------------------------

        self.draw_quad(
            black,
            [
                (x1, y2, z2),
                (x2, y2, z2),
                (x2, y2, z1),
                (x1, y2, z1),
            ]
        )


        # ----------------------------------------------------------------
        # BOTTOM
        # ----------------------------------------------------------------

        self.draw_quad(
            black,
            [
                (x1, y1, z1),
                (x2, y1, z1),
                (x2, y1, z2),
                (x1, y1, z2),
            ]
        )


        # ----------------------------------------------------------------
        # STICKER SIZE
        # ----------------------------------------------------------------

        gap = 0.08

        a = half - gap


        # ----------------------------------------------------------------
        # FRONT STICKER
        # ----------------------------------------------------------------

        if "F" in stickers:

            color = stickers["F"]


            self.draw_quad(
                color,
                [
                    (x - a, y - a, z2 + 0.006),
                    (x + a, y - a, z2 + 0.006),
                    (x + a, y + a, z2 + 0.006),
                    (x - a, y + a, z2 + 0.006),
                ]
            )


        # ----------------------------------------------------------------
        # BACK STICKER
        # ----------------------------------------------------------------

        if "B" in stickers:

            color = stickers["B"]


            self.draw_quad(
                color,
                [
                    (x + a, y - a, z1 - 0.006),
                    (x - a, y - a, z1 - 0.006),
                    (x - a, y + a, z1 - 0.006),
                    (x + a, y + a, z1 - 0.006),
                ]
            )


        # ----------------------------------------------------------------
        # RIGHT STICKER
        # ----------------------------------------------------------------

        if "R" in stickers:

            color = stickers["R"]


            self.draw_quad(
                color,
                [
                    (x2 + 0.006, y - a, z + a),
                    (x2 + 0.006, y - a, z - a),
                    (x2 + 0.006, y + a, z - a),
                    (x2 + 0.006, y + a, z + a),
                ]
            )


        # ----------------------------------------------------------------
        # LEFT STICKER
        # ----------------------------------------------------------------

        if "L" in stickers:

            color = stickers["L"]


            self.draw_quad(
                color,
                [
                    (x1 - 0.006, y - a, z - a),
                    (x1 - 0.006, y - a, z + a),
                    (x1 - 0.006, y + a, z + a),
                    (x1 - 0.006, y + a, z - a),
                ]
            )


        # ----------------------------------------------------------------
        # TOP STICKER
        # ----------------------------------------------------------------

        if "U" in stickers:

            color = stickers["U"]


            self.draw_quad(
                color,
                [
                    (x - a, y2 + 0.006, z + a),
                    (x + a, y2 + 0.006, z + a),
                    (x + a, y2 + 0.006, z - a),
                    (x - a, y2 + 0.006, z - a),
                ]
            )


        # ----------------------------------------------------------------
        # BOTTOM STICKER
        # ----------------------------------------------------------------

        if "D" in stickers:

            color = stickers["D"]


            self.draw_quad(
                color,
                [
                    (x - a, y1 - 0.006, z - a),
                    (x + a, y1 - 0.006, z - a),
                    (x + a, y1 - 0.006, z + a),
                    (x - a, y1 - 0.006, z + a),
                ]
            )


# ============================================================================
# DRAW WHOLE CUBE
# ============================================================================

    def draw_cube(self):

        positions = [
            -1.02,
            0.0,
            1.02
        ]


        for xi, x in enumerate(
            positions
        ):

            for yi, y in enumerate(
                positions
            ):

                for zi, z in enumerate(
                    positions
                ):

                    stickers = {}


                    # ----------------------------------------------------
                    # FRONT
                    # ----------------------------------------------------

                    if zi == 2:

                        row = 2 - yi
                        col = xi


                        stickers["F"] = (
                            self.get_sticker_color(
                                "F",
                                row,
                                col
                            )
                        )


                    # ----------------------------------------------------
                    # BACK
                    # ----------------------------------------------------

                    if zi == 0:

                        row = 2 - yi
                        col = 2 - xi


                        stickers["B"] = (
                            self.get_sticker_color(
                                "B",
                                row,
                                col
                            )
                        )


                    # ----------------------------------------------------
                    # RIGHT
                    # ----------------------------------------------------

                    if xi == 2:

                        row = 2 - yi
                        col = 2 - zi


                        stickers["R"] = (
                            self.get_sticker_color(
                                "R",
                                row,
                                col
                            )
                        )


                    # ----------------------------------------------------
                    # LEFT
                    # ----------------------------------------------------

                    if xi == 0:

                        row = 2 - yi
                        col = zi


                        stickers["L"] = (
                            self.get_sticker_color(
                                "L",
                                row,
                                col
                            )
                        )


                    # ----------------------------------------------------
                    # TOP
                    # ----------------------------------------------------

                    if yi == 2:

                        row = zi
                        col = xi


                        stickers["U"] = (
                            self.get_sticker_color(
                                "U",
                                row,
                                col
                            )
                        )


                    # ----------------------------------------------------
                    # BOTTOM
                    # ----------------------------------------------------

                    if yi == 0:

                        row = 2 - zi
                        col = xi


                        stickers["D"] = (
                            self.get_sticker_color(
                                "D",
                                row,
                                col
                            )
                        )


                    self.draw_cubie(
                        x,
                        y,
                        z,
                        stickers
                    )


# ============================================================================
# OPENGL SETUP
# ============================================================================

    def setup_opengl(self):

        glEnable(
            GL_DEPTH_TEST
        )

        glEnable(
            GL_CULL_FACE
        )

        glClearColor(
            0.04,
            0.04,
            0.04,
            1.0
        )


# ============================================================================
# CAMERA
# ============================================================================

    def setup_camera(
        self,
        width,
        height
    ):

        if height == 0:

            height = 1


        glViewport(
            0,
            0,
            width,
            height
        )


        glMatrixMode(
            GL_PROJECTION
        )

        glLoadIdentity()


        gluPerspective(
            45.0,
            width / height,
            0.1,
            100.0
        )


        glMatrixMode(
            GL_MODELVIEW
        )

        glLoadIdentity()


        glTranslatef(
            0,
            0,
            -self.camera_distance
        )


        glRotatef(
            self.camera_x,
            1,
            0,
            0
        )


        glRotatef(
            self.camera_y,
            0,
            1,
            0
        )


# ============================================================================
# RENDER
# ============================================================================

    def render(
        self,
        width,
        height
    ):

        glClear(
            GL_COLOR_BUFFER_BIT
            | GL_DEPTH_BUFFER_BIT
        )


        self.setup_camera(
            width,
            height
        )


        self.draw_cube()


# ============================================================================
# MOUSE BUTTON
# ============================================================================

    def mouse_button(
        self,
        window,
        button,
        action,
        mods
    ):

        if (
            button
            != glfw.MOUSE_BUTTON_LEFT
        ):

            return


        if action == glfw.PRESS:

            self.dragging = True


            (
                self.last_mouse_x,
                self.last_mouse_y
            ) = glfw.get_cursor_pos(
                window
            )


        elif action == glfw.RELEASE:

            self.dragging = False


# ============================================================================
# MOUSE MOVE
# ============================================================================

    def mouse_move(
        self,
        window,
        xpos,
        ypos
    ):

        if not self.dragging:

            return


        dx = (
            xpos
            - self.last_mouse_x
        )


        dy = (
            ypos
            - self.last_mouse_y
        )


        self.camera_y += (
            dx * ROTATION_SPEED
        )


        self.camera_x += (
            dy * ROTATION_SPEED
        )


        if self.camera_x > 89:

            self.camera_x = 89


        if self.camera_x < -89:

            self.camera_x = -89


        self.last_mouse_x = xpos

        self.last_mouse_y = ypos


# ============================================================================
# SCROLL
# ============================================================================

    def scroll(
        self,
        window,
        xoffset,
        yoffset
    ):

        self.camera_distance -= (
            yoffset * 0.5
        )


        if self.camera_distance < 5:

            self.camera_distance = 5


        if self.camera_distance > 25:

            self.camera_distance = 25


# ============================================================================
# KEYBOARD
# ============================================================================

    def key(
        self,
        window,
        key,
        scancode,
        action,
        mods
    ):

        if action != glfw.PRESS:

            return


        # ----------------------------------------------------------------
        # ALGORITHM NAVIGATION
        # ----------------------------------------------------------------

        if key == glfw.KEY_RIGHT:

            self.next_algorithm()


        elif key == glfw.KEY_LEFT:

            self.previous_algorithm()


        # ----------------------------------------------------------------
        # ROTATE VIEW WITH WASD
        # ----------------------------------------------------------------

        elif key == glfw.KEY_A:

            self.camera_y -= KEY_ROTATION


        elif key == glfw.KEY_D:

            self.camera_y += KEY_ROTATION


        elif key == glfw.KEY_W:

            self.camera_x -= KEY_ROTATION


        elif key == glfw.KEY_S:

            self.camera_x += KEY_ROTATION


        # ----------------------------------------------------------------
        # FIRST ALGORITHM
        # ----------------------------------------------------------------

        elif key == glfw.KEY_HOME:

            if self.algorithms:

                self.current_index = 0

                self.show_algorithm()


        # ----------------------------------------------------------------
        # LAST ALGORITHM
        # ----------------------------------------------------------------

        elif key == glfw.KEY_END:

            if self.algorithms:

                self.current_index = (
                    len(self.algorithms) - 1
                )

                self.show_algorithm()


        # ----------------------------------------------------------------
        # QUIT
        # ----------------------------------------------------------------

        elif key == glfw.KEY_ESCAPE:

            glfw.set_window_should_close(
                window,
                True
            )


# ============================================================================
# MAIN
# ============================================================================

def main():

    # ------------------------------------------------------------------------
    # INITIALIZE GLFW
    # ------------------------------------------------------------------------

    if not glfw.init():

        raise RuntimeError(
            "Could not initialize GLFW."
        )


    # ------------------------------------------------------------------------
    # CREATE WINDOW
    # ------------------------------------------------------------------------

    window = glfw.create_window(
        WINDOW_WIDTH,
        WINDOW_HEIGHT,
        "CubeTool OpenGL Renderer",
        None,
        None
    )


    if not window:

        glfw.terminate()

        raise RuntimeError(
            "Could not create OpenGL window."
        )


    glfw.make_context_current(
        window
    )


    glfw.swap_interval(1)


    # ------------------------------------------------------------------------
    # CREATE RENDERER
    # ------------------------------------------------------------------------

    renderer = CubeRenderer()


    renderer.setup_opengl()


    # ------------------------------------------------------------------------
    # CALLBACKS
    # ------------------------------------------------------------------------

    glfw.set_mouse_button_callback(
        window,
        renderer.mouse_button
    )


    glfw.set_cursor_pos_callback(
        window,
        renderer.mouse_move
    )


    glfw.set_scroll_callback(
        window,
        renderer.scroll
    )


    glfw.set_key_callback(
        window,
        renderer.key
    )


    # ------------------------------------------------------------------------
    # LOAD ALGORITHM FILE
    # ------------------------------------------------------------------------

    if len(sys.argv) > 1:

        renderer.load_file(
            sys.argv[1]
        )


    # ------------------------------------------------------------------------
    # MAIN LOOP
    # ------------------------------------------------------------------------

    while not glfw.window_should_close(
        window
    ):

        width, height = (
            glfw.get_framebuffer_size(
                window
            )
        )


        renderer.render(
            width,
            height
        )


        glfw.swap_buffers(
            window
        )


        glfw.poll_events()


    # ------------------------------------------------------------------------
    # CLEANUP
    # ------------------------------------------------------------------------

    glfw.destroy_window(
        window
    )

    glfw.terminate()


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":

    main()
