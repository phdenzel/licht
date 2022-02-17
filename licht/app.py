"""
licht.app

@author: phdenzel
"""
import os
import logging
import signal
import licht
from licht.rest import LichtClient
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")
from gi.repository import Gtk, Gdk, AppIndicator3


class LichtIndicator(object):

    def __init__(self, root, app_name='licht', icon_path=None):
        self.app = root
        self.app_name = app_name
        if icon_path is not None:
            self.icon_path = icon_path
        else:
            self.icon_path = licht.icon_path
        self.icon_path = os.path.expanduser(self.icon_path)
        logging.info(f'Loading icon {self.icon_path}')
        self.indicator = AppIndicator3.Indicator.new(
            self.app_name, self.icon_path,
            AppIndicator3.IndicatorCategory.OTHER)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        menu = self.generate_menu()
        self.indicator.set_menu(menu)
        self.indicator.get_menu().connect('show', self.update)

    def update(self, event):
        """
        Update all submenus
        Signal: <show>, connects to <Menu>
        """
        menu = self.indicator.get_menu()
        data = self.app.data
        for i, item in enumerate(menu.get_children()):
            submenu = item.get_submenu()
            if submenu:
                data_attr = data.__getattribute__(submenu.get_name())
                self.update_submenu(submenu, data_attr)

    def generate_menu(self):
        """
        Create a Menu containing submenus for a LichtClient's data fetch of
        lights, groups, and scenes
        """
        menu = Gtk.Menu()
        # get data once and store
        data = self.app.data
        if data.lights is not None:
            item = self.menu_item("Lights")
            submenu = self.generate_submenu(data.lights.names,
                                            device_id='lights/{}:{}')
            item.set_submenu(submenu)
            self.update_submenu(submenu, data.lights)
            menu.append(item)
            menu.append(self.separator)
        if data.groups is not None:
            item = self.menu_item("Rooms")
            submenu = self.generate_submenu(data.groups.names,
                                            device_id='groups/{}:{}')
            item.set_submenu(submenu)
            self.update_submenu(submenu, data.groups)
            item.set_submenu(submenu)
            menu.append(item)
            menu.append(self.separator)
        if data.scenes is not None:
            item = self.menu_item("Scenes")
            submenu = self.generate_submenu(data.scenes.names,
                                            device_id='scenes/{}:{}',
                                            on_off_toggle=False,
                                            bri_scale=False,
                                            ct_scale=False)
            item.set_submenu(submenu)
            menu.append(item)
            menu.append(self.separator)
        item = Gtk.MenuItem()
        item.set_label("Quit")
        item.connect("activate", self.app.on_exit, '')
        menu.append(item)
        menu.show_all()
        return menu

    def generate_submenu(self, name_index, device_id='lights/{}:{}',
                         on_off_toggle=True, bri_scale=True, ct_scale=True):
        """
        Create a Menu and populate it with MenuItems corresponding to
        a name index from data fetch
        """
        submenu = Gtk.Menu()
        submenu.set_name(device_id.split('/')[0])
        for index, label in name_index.items():
            # Toggle on/off
            if on_off_toggle:
                check_item = self.check_item(label, bold=True, indent=0,
                                             device_id=device_id.format(index, 'on'),
                                             connect=('toggled',
                                                      self.app.on_toggle_change))
                submenu.append(check_item)
            else:
                menuitem = self.menu_item(label, bold=False, indent=0,
                                          device_id=device_id.format(index, 'scene'),
                                          connect=('activate',
                                                   self.app.on_activation_change))
                submenu.append(menuitem)
            # Brightness scale
            if bri_scale:
                bri_limits = licht.constants.limits_transf['bri']
                slider_item = self.slider_item(bri_limits[0], bri_limits[1], 1, _type='%',
                                               device_id=device_id.format(index, 'bri'),
                                               connect=("value-changed",
                                                        self.app.on_scroll_change))
                submenu.append(slider_item)
            # Color temperature scale
            if ct_scale:
                ct_limits = licht.constants.limits_transf['ct']
                slider_item = self.slider_item(ct_limits[0], ct_limits[1], 5, _type="Temp",
                                               device_id=device_id.format(index, 'ct'),
                                               connect=("value-changed",
                                                        self.app.on_scroll_change))
                submenu.append(slider_item)
                submenu.append(self.separator)
        return submenu

    def update_submenu(self, menu, data):
        """
        Update all MenuItems of a submenu corresponding to its properties
        """
        for menu_item in menu.get_children():
            cls_name = menu_item.__class__.__name__
            if cls_name == 'SeparatorMenuItem':
                continue
            elif cls_name == 'CheckMenuItem':  # Title on/off
                device_id = menu_item.get_name()
                get_subpath, state_attr = device_id.split(':')
                idx = get_subpath.split('/')[-1]
                state = data[idx][data.state_cmd][state_attr]
                menu_item.set_active(state)
            elif cls_name == 'MenuItem' and menu_item.get_children():  # Scale
                device_id = menu_item.get_name()
                get_subpath, state_attr = device_id.split(':')
                idx = get_subpath.split('/')[-1]
                if data.state_cmd not in data[idx]:
                    continue
                state = data[idx][data.state_cmd][state_attr]
                # convert state depending on state_attr
                state = licht.constants.transformations[state_attr][0](state)
                slider = menu_item.get_children()[0]
                slider.set_value(state)

    def menu_item(self, label, checkbox=False, indent=False, bold=False,
                  device_id=None, connect=None):
        """
        Create a MenuItem and set its properties
        """
        menuitem = Gtk.MenuItem()
        if indent:
            for i in range(int(indent)):
                label = f"\t{label}"
        if label:
            menuitem.set_label(label)
            if bold:
                menuitem.get_children()[0].set_markup(f"<b>{label}</b>")
        if device_id:
            menuitem.set_name(device_id)
        if connect is not None:
            menuitem.connect(*connect)
        return menuitem

    def check_item(self, label, indent=False, bold=False, device_id=None,
                   connect=None):
        """
        Create a CheckMenuItem and set its properties
        """
        menuitem = Gtk.CheckMenuItem()
        if indent:
            for i in range(int(indent)):
                label = f"\t{label}"
        if label:
            menuitem.set_label(label)
            if bold:
                menuitem.get_children()[0].set_markup(f"<b>{label}</b>")
        if device_id:
            menuitem.set_name(device_id)
        if connect is not None:
            menuitem.connect(*connect)
        return menuitem

    def slider_item(self, range_min=0, range_max=100, range_inc=1,
                    device_id=None, _type='%', connect=None):
        """
        Create a MenuItem with a Scale widget and set its properties
        """
        slider_menu = self.menu_item('')
        slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL,
                                          range_min, range_max, range_inc)
        slider.set_hexpand(True)
        if connect is not None:
            slider.connect(*connect)
        if '%' in _type:
            slider.connect('format-value', self.slider_format(ps=_type))
        if "Temp" in _type:
            slider.connect('format-value', self.slider_format(title=_type))
        slider.set_value_pos(0)  # on the left
        if device_id:
            slider_menu.set_name(device_id)
            slider.set_name(device_id)
        slider_menu.add(slider)
        slider_menu.add_events(Gdk.EventMask.SCROLL_MASK)
        slider_menu.connect('scroll-event', self.app.on_scroll)
        slider_menu.connect('button-press-event', self.app.on_scroll_click)
        return slider_menu

    def slider_format(self, title="", ps=""):
        """
        Function factory for triggering formatting of a Scale widget's value
        Signal: <format-value>, connects to <Gtk.Scale>
        """
        def scale_formatter(widget, value, title=title, ps=ps):
            formatted_str = "{} {:3d}{} ".format(title, int(value), ps)
            return formatted_str
        return scale_formatter

    @property
    def separator(self):
        """
        Wrapper for SeparatorMenuItem
        """
        return Gtk.SeparatorMenuItem()


class LichtApplet(Gtk.Application):
    def __init__(self, app_name='licht', client=None):
        self.app_name = app_name
        self.client = client
        if self.client is None:
            self.client = LichtClient(licht.bridge_ip)
        self.indicator = LichtIndicator(self)

    @property
    def data(self):
        """
        Trigger GET request for data fetch by client
        """
        if hasattr(self, 'client'):
            data = self.client.fetch_data()
            self.data_cache = data
            return data

    def on_toggle_change(self, widget):
        """
        Trigger PUT request for state change by client.
        State change specifications are drawn from the
        CheckMenuItem's name attribute and state.
        Signal: <value-changed>, connects to <CheckMenuItem>
        """
        device_id = widget.get_name()
        get_subpath, state_attr = device_id.split(':')
        idx = get_subpath.split('/')[-1]
        data = self.data_cache.from_path(get_subpath)
        data_state = data[idx][data.state_cmd][state_attr]
        toggle_state = widget.get_active()
        if data_state != toggle_state:
            update = {state_attr: toggle_state}
            logging.info(f"PUT:  path: {data.put_path}\tbody: {update}")
            self.client.change_state(data=data, update=update)

    def on_activation_change(self, widget):
        """
        Trigger PUT request for state change by client.
        State change specifications are drawn from the
        MenuItem's name attribute.
        Signal: <activate>, connects to <MenuItem>
        """
        device_id = widget.get_name()
        get_subpath, state_attr = device_id.split(':')
        idx = get_subpath.split('/')[-1]
        data = self.data_cache.from_path(get_subpath)
        update = {state_attr: idx}
        logging.info(f"PUT:  path: {data.put_path}\tbody: {update}")
        self.client.change_state(subpath=data.put_path, update=update)

    def on_scroll_change(self, widget):
        """
        Trigger PUT request for state change by client.
        State change specifications are drawn from the
        MenuItem's name attribute and its Scale widget state.
        Signal: <value-changed>, connects to <MenuItem>
        """
        device_id = widget.get_name()
        get_subpath, state_attr = device_id.split(':')
        idx = get_subpath.split('/')[-1]
        data = self.data_cache.from_path(get_subpath)
        data_state = data[idx][data.state_cmd][state_attr]
        scroll_state = licht.constants.transformations[state_attr][1](
            widget.get_value())
        if data[idx][data.state_cmd]['on'] and (data_state != scroll_state):
            update = {state_attr: scroll_state}
            logging.info(f"PUT:  path: {data.put_path}\tbody: {update}")
            self.client.change_state(data=data, update=update)

    def on_scroll_click(self, widget, event):
        """
        Manipulate the Scale widgets of a MenuItem by propagating
        the cursor position to the underlying Scale widget.
        Signal: <button-press-event>, connects to <MenuItem>
        """
        scale = widget.get_children()[0]
        current_val = scale.get_value()
        range_min = scale.get_adjustment().get_lower()
        range_max = scale.get_adjustment().get_upper()
        walloc = widget.get_allocation()
        alloc = scale.get_allocation()
        spacing = walloc.width - alloc.width
        scale_offset = scale.get_layout().get_pixel_size()[0] + spacing
        scale_width = alloc.width - (scale_offset - alloc.x)
        cursor_x = (event.x - scale_offset) / scale_width
        val = licht.utils.linear_transformation(
            cursor_x, 0, 1, range_min, range_max,
            allow_out_of_bounds=False, as_int=True)
        if val != current_val:
            scale.set_value(val)

    def on_scroll(self, widget, event):
        """
        Manipulate the Scale widget of a MenuItem.
        Signal: <scroll-event>, connects to <MenuItem>
        """
        scale = widget.get_children()[0]
        current_val = scale.get_value()
        range_min = scale.get_adjustment().get_lower()
        range_max = scale.get_adjustment().get_upper()
        range_inc = scale.get_adjustment().get_step_increment()
        if event.direction == Gdk.ScrollDirection.UP:
            val = min(current_val+range_inc, range_max)
        elif event.direction == Gdk.ScrollDirection.DOWN:
            val = max(current_val-range_inc, range_min)
        scale.set_value(val)

    def on_exit(self, widget, event):
        """
        Trigger exit from applet.
        Signal: <activate>
        """
        Gtk.main_quit()

    def run(self):
        """
        Run Gtk main
        """
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        Gtk.main()


if __name__ == "__main__":
    licht_applet = LichtApplet()
