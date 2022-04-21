import os
import sys
import imgui
import glfw
import OpenGL.GL as gl
import webbrowser
import json
from operator import attrgetter
from dataclasses import dataclass
from imgui.integrations.glfw import GlfwRenderer

path_to_font = "JetBrainsMono-Regular.ttf"
chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
was_double_clicked = False
should_reset_scrollbar = False
wage_sorting_descending = None
double_click_start_x = 0
double_click_start_y = 0



def sort_by_criteria(posts: list, criteria: str, descending: bool = True):
    posts.sort(reverse=descending, key=attrgetter(criteria))
    return posts


@dataclass(order=True)
class Sludinajums:
    # sort_index: int = field(init=False, repr=False)
    amats: str
    autors: str
    min_alga: int
    max_alga: int
    link: str

    # def __post_init__(self):
    #     self.sort_index = self.min_alga


def display_list_of_companies(jobs=None, author_list=None):
    for author in author_list:
        clicked, state = imgui.menu_item(f"{author[0]}: {str(author[1])}", "", False, True)
        if clicked:
            filter_by_keywords(jobs, keywords=author[0])


def restore_original(jobs):
    jobs.clear()

    with open("original.json", "r") as f:
        data = json.load(f)
        for element in data:
            values = list(element.values())
            jobs.append(Sludinajums(values[0], values[1], values[2], values[3], values[4]))


def filter_by_keywords(posts: list, keywords: str):
    print(keywords)
    keyword_list = keywords.split()
    posts_copy = posts.copy()  # this is needed because otherwise removing is very FUCKY
    for job in posts_copy:
        x = job.autors.upper() + job.amats.upper()
        for keyword in keyword_list:
            y = keyword.upper()
            if y not in x:
                posts.remove(job)
                break


def fill_table(job_postings=None):
    imgui.columns(4, "tests")
    for i in range(len(job_postings)):
        imgui.separator()
        imgui.text(str(job_postings[i].min_alga))
        imgui.next_column()
        imgui.text(job_postings[i].amats)
        imgui.next_column()
        imgui.text(job_postings[i].autors)
        imgui.next_column()
        url = job_postings[i].link

        if imgui.button(f"  {i}   ", width=150, height=36):
            webbrowser.get(chrome_path).open(url)
        imgui.next_column()
    imgui.columns(1)


def frame_commands(jobs=None, author_list=None):
    global double_click_start_x
    global double_click_start_y
    global was_double_clicked
    global wage_sorting_descending
    global should_reset_scrollbar

    #index = int(double_click_start_y + imgui.get_scroll_y() - 102) // 42

    scroll_pos = 0
    imgui.set_next_window_size(1500, 800)
    imgui.set_next_window_position(10, 60)
    imgui.STYLE_WINDOW_BORDERSIZE = 0.0
    imgui.begin("a windowss",
                flags=imgui.WINDOW_NO_MOVE |
                      imgui.WINDOW_NO_TITLE_BAR |
                      imgui.WINDOW_NO_RESIZE
                      )

    # ONE ROW APPROX 44 PX
    imgui.begin_child("nosaukumi", 1500, 50, border=False)
    imgui.columns(4, "tests")
    imgui.set_column_offset(1, 120)
    imgui.set_column_offset(2, 1050)
    imgui.set_column_offset(3, 1300)

    # COLUMN NAMES - MAYBE CHANGE THEM TO SEPARATE WINDOW AFTER!
    imgui.text("Min wage")
    imgui.next_column()
    imgui.text("Job description")
    imgui.next_column()
    imgui.text("Posted by")
    imgui.next_column()
    imgui.text("link")
    imgui.columns(1)
    imgui.end_child()

    imgui.begin_child("main table", 1450, 700, border=False)

    # print(f" content region available - {imgui.get_content_region_available()}")
    # print(f" window content region max - {imgui.get_window_content_region_max()}")
    # print(f"window position = {imgui.get_window_position()}")
    # print(f"window content region min  = {imgui.get_window_content_region_min()}")
    # print(f"max scroll y {imgui.get_scroll_max_y()}")
    # print(f" cursor pos = {imgui.get_cursor_pos()}")
    # print(f"current context = {imgui.get_current_context()}")

    imgui.columns(4, "tests")
    imgui.set_column_offset(1, 120)
    imgui.set_column_offset(2, 1050)
    imgui.set_column_offset(3, 1300)
    fill_table(job_postings=jobs)
    imgui.columns(1)

    # + 8 ja border=True
    table_window_y_position = imgui.get_window_position()[1]
    scroll_pos = imgui.get_scroll_y()
    scroll_coefficient = 1.123
    table_row_height = 44.91
    # i dont even know how i got to these numbers, but they work and it wasnt fun
    index = int(imgui.get_mouse_pos()[1] + round(scroll_pos * scroll_coefficient) - table_window_y_position) // table_row_height

    if should_reset_scrollbar:
        imgui.set_scroll_y(0)
        should_reset_scrollbar = False

    imgui.end_child()

    if imgui.is_mouse_double_clicked():
        current_mouse_x = imgui.get_mouse_pos()[0]
        current_mouse_y = imgui.get_mouse_pos()[1]
        if 140 < current_mouse_x < 1068 and 130 < current_mouse_y < 830:
            link = jobs[int(index)].link
            webbrowser.get(chrome_path).open(link)
        if 9 < current_mouse_x < 138 and 59 < current_mouse_y < 121:
            if wage_sorting_descending is None:
                wage_sorting_descending = False
            else:
                wage_sorting_descending = not wage_sorting_descending
            sort_by_criteria(posts=jobs, criteria="min_alga", descending=wage_sorting_descending)
            should_reset_scrollbar = True

    # if was_double_clicked:
    #     #link = jobs[index].link
    #     print("klikd")
    #     imgui.open_popup("popups")
    #     imgui.set_next_window_size(800, 100)
    #     if imgui.begin_popup("popups"):
    #         window_x = imgui.get_window_position()[0]
    #         window_y = imgui.get_window_position()[1]
    #         window_width = imgui.get_window_width()
    #         window_height = imgui.get_window_height()
    #         if imgui.is_mouse_clicked() and not imgui.is_mouse_double_clicked():
    #             if imgui.get_mouse_pos()[0] < window_x or imgui.get_mouse_pos()[0] > window_x + window_width:
    #                 was_double_clicked = False
    #             elif imgui.get_mouse_pos()[1] < window_y or imgui.get_mouse_pos()[1] > window_y + window_height:
    #                 was_double_clicked = False
    #             else:
    #                 webbrowser.get(chrome_path).open(link)
    #
    #         imgui.text(f"window x = {window_x}, window y = {window_y} \n {link}")
    #         imgui.end_popup()

    imgui.end()

    if imgui.begin_main_menu_bar():
        # first menu dropdown
        if imgui.begin_menu('File', True):
            imgui.menu_item('New', 'Ctrl+N', False, True)
            imgui.menu_item('Open ...', 'Ctrl+O', False, True)

            # submenu
            if imgui.begin_menu('Open Recent', True):
                imgui.menu_item('doc.txt', None, False, True)
                imgui.end_menu()

            imgui.end_menu()

        imgui.same_line(spacing=20)
        if imgui.begin_menu("Sort by:", True):
            clicked, state = imgui.menu_item('Wage, highest first', 'Ctrl+N', False, True)
            if clicked:
                sort_by_criteria(jobs, criteria="min_alga", descending=True)
                should_reset_scrollbar = True
            klikd, steit = imgui.menu_item('Wage, lowest first', 'Ctrl+N', False, True)
            if klikd:
                sort_by_criteria(jobs, criteria="min_alga", descending=False)
                should_reset_scrollbar = True
            imgui.end_menu()

        imgui.same_line(spacing=20)
        imgui.set_next_window_size(800, 500)
        if imgui.begin_menu("Top companies:", True):
            for author in author_list:
                clicked, state = imgui.menu_item(f"{author[0]}: {str(author[1])}", "", False, True)
                if clicked:
                    restore_original(jobs)
                    filter_by_keywords(jobs, keywords=author[0])
                    wage_sorting_descending = None
                    should_reset_scrollbar = True

            imgui.end_menu()

        # helpers that display info on the top main menu bar
        # imgui.same_line(spacing=20)
        # imgui.text(f"cursor pos = {imgui.get_mouse_pos()}")
        # imgui.same_line(spacing=20)
        # imgui.text(f"scroll pos = {scroll_pos}")
        # imgui.same_line(spacing=10)
        # imgui.text(f"index = {index}")

        imgui.same_line(spacing=800)
        imgui.text("Search for:")
        imgui.same_line(spacing=20)
        text_val = "keywords"
        changed, text_val = imgui.input_text(
                         "serch:",
                         text_val,
                         100,
                         imgui.INPUT_TEXT_AUTO_SELECT_ALL |
                         imgui.INPUT_TEXT_ENTER_RETURNS_TRUE)
        if changed:
            if text_val == "keywords" or text_val == "":
                restore_original(jobs)
                wage_sorting_descending = None
                should_reset_scrollbar = True
            else:
                restore_original(jobs)
                filter_by_keywords(jobs, text_val)
                wage_sorting_descending = None
                should_reset_scrollbar = True

        imgui.end_main_menu_bar()


def render_frame(impl, window, font, jobs, author_list=None):
    glfw.poll_events()
    impl.process_inputs()
    imgui.new_frame()

    gl.glClearColor(0.1, 0.1, 0.1, 1)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    if font is not None:
        imgui.push_font(font)
    frame_commands(jobs, author_list)
    if font is not None:
        imgui.pop_font()

    imgui.render()
    impl.render(imgui.get_draw_data())
    glfw.swap_buffers(window)


def impl_glfw_init():
    width, height = 1600, 900
    window_name = "minimal ImGui/GLFW3 example"

    if not glfw.init():
        print("Could not initialize OpenGL context")
        sys.exit(1)

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    window = glfw.create_window(int(width), int(height), window_name, None, None)
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        sys.exit(1)

    return window


def main(jobs=None, author_list=None):
    imgui.create_context()
    window = impl_glfw_init()

    impl = GlfwRenderer(window)

    io = imgui.get_io()
    jb = io.fonts.add_font_from_file_ttf(path_to_font, 30) if path_to_font is not None else None
    impl.refresh_font_texture()

    while not glfw.window_should_close(window):
        render_frame(impl, window, jb, jobs, author_list)

    impl.shutdown()
    glfw.terminate()


if __name__ == '__main__':
    main()