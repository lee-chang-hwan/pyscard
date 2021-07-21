"""Smartcard manager
"""

# Use Tkinter for python 2, tkinter for python 3
import tkinter as tk
import tkinter.scrolledtext as tkst
import tkinter.messagebox as tkmb
from tkinter import ttk
from tkinter import Menu

from smartcard.System import readers
from smartcard.util import toHexString, toBytes

from scm.gp import GP
from scm.apdu import *

class Page(object):
    """Page class
    This class is a basic class of the smartcard manager's UI
    """

    def __init__(self, root, debugger=None, connector=None):
        """Construct new Page.

        Args:
            root -- the tkinter
            debugger -- the DebuggerWidget instance
            connector -- the Connector instance
        """
        self.root = root
        self.debugger = debugger
        self.connector = connector


class MainPage(Page):
    """MainPage class
    The smartcard manager's Main UI
    """

    def __init__(self, root):
        """Construct new Page.
        """
        super().__init__(root)      #Call a super class's constructor
        self.debugger = DebuggerWidget()
        self.connector = Connector(self.debugger)
        self.root.title('Main')
        self._create_widgets()
        self.debugger.set_debug_widget(self.st_log)

    def _create_widgets(self):
        """Creates widgets
        """
        self._create_apdu_frame()
        self._create_app_frame()
        self._create_menu()

    def _create_menu(self):
        """Creates menus
        """
        self.menu_bar = Menu(self.root)        # Create a menu
        self.root.config(menu=self.menu_bar)
        self.menu_file = Menu(self.menu_bar, tearoff=0)       # Create the File Menu
        self.menu_file.add_command(label="Exit", command=self.click_exit) # Add the "Exit" menu and bind a function
        self.menu_bar.add_cascade(label="File", menu=self.menu_file)
        self.menu_help = Menu(self.menu_bar, tearoff=0)
        self.menu_help.add_command(label="About", command=self.click_about)   # Add the "About" menu and bind a function
        self.menu_bar.add_cascade(label="Help", menu=self.menu_help)

    def _create_apdu_frame(self):
        """Creates an apdu frame
        """
        self.frame_apdu = tk.Frame(self.root)
        self.frame_apdu.grid(column=0, row=0)
        self.label_reader = ttk.Label(self.frame_apdu, text='Reader')
        self.label_reader.grid(column=0, row=0)
        self.str_reader_name = tk.StringVar()        # String variable
        self.combo_reader = ttk.Combobox(self.frame_apdu, width=30, state='readonly'
                                         , textvariable=self.str_reader_name)   # Create a combobox
        self.combo_reader.grid(column=1, row=0)
        self.combo_reader['values'] = self.connector.get_all_connectors()
        try:
            self.combo_reader.current(0)
        except Exception:
            pass
        self.button_reset = ttk.Button(self.frame_apdu, text='Reset...', command=self.click_reset)   # Create a button
        self.button_reset.grid(column=2, row=0)
        self.st_log = tkst.ScrolledText(self.frame_apdu, width=50, height=20, wrap=tk.WORD)     # Create a scrolledtext5
        self.st_log.grid(column=0, row=1, columnspan=3)
        self.entry_cmd = tk.Entry(self.frame_apdu, width=40)                                # Create a entry
        self.entry_cmd.grid(column=0, row=2, columnspan=2)
        self.entry_cmd.focus_set()
        self.button_cmd = ttk.Button(self.frame_apdu, text='Send...', command=self.click_send)   # Create a button
        self.button_cmd.grid(column=2, row=2)

    def _create_app_frame(self):
        """Creates applications frame
        """
        self.frame_app = tk.Frame(self.root)
        self.frame_app.grid(column=1, row=0)
        self.lable_enc = ttk.Label(self.frame_app, text='ENC')
        self.lable_enc.grid(column=0, row=0)
        self.entry_enc = tk.Entry(self.frame_app)
        self.entry_enc.config(width='33')
        self.entry_enc.grid(column=1, row=0, columnspan=2)
        self.entry_enc.insert(tk.INSERT, '404142434445464748494A4B4C4D4E4F')
        self.label_mac = ttk.Label(self.frame_app, text='MAC')
        self.label_mac.grid(column=0, row=1)
        self.entry_mac = tk.Entry(self.frame_app)
        self.entry_mac.config(width='33')
        self.entry_mac.grid(column=1, row=1, columnspan=2)
        self.entry_mac.insert(tk.INSERT, '404142434445464748494A4B4C4D4E4F')
        self.label_dek = ttk.Label(self.frame_app, text='DEK')
        self.label_dek.grid(column=0, row=2)
        self.entry_dek = tk.Entry(self.frame_app)
        self.entry_dek.config(width='33')
        self.entry_dek.grid(column=1, row=2, columnspan=2)
        self.entry_dek.insert(tk.INSERT, '404142434445464748494A4B4C4D4E4F')
        self.sv_rule = tk.StringVar()
        self.radio_none = tk.Radiobutton(self.frame_app, text=gp.NO_DERIVATION
                                         , variable=self.sv_rule, value=gp.NO_DERIVATION)
        self.radio_none.grid(column=0, row=3)
        self.radio_cpg201 = tk.Radiobutton(self.frame_app, text=gp.CPG201
                                           , variable=self.sv_rule, value=gp.CPG201)
        self.radio_cpg201.config(state='disabled')
        self.radio_cpg201.grid(column=1, row=3)
        self.radio_cpg211 = tk.Radiobutton(self.frame_app, text=gp.CPG211
                                           , variable=self.sv_rule, value=gp.CPG211)
        self.radio_cpg211.config(state='disabled')
        self.radio_cpg211.grid(column=2, row=3)
        self.radio_none.select()
        self.treeveiw_apps = ttk.Treeview(self.frame_app, height=9)
        self.treeveiw_apps['columns'] = ('Life Cycle State', 'Privilieges')
        self.treeveiw_apps.heading('#0', text='AID')
        self.treeveiw_apps.heading('#1', text='Life Cycle State')
        self.treeveiw_apps.heading('#2', text='Privilieges')        
        self.treeveiw_apps.column('#0', width=200)
        self.treeveiw_apps.column('#1', width=50)
        self.treeveiw_apps.column('#2', width=50)
        self.tvi_isd = self.treeveiw_apps.insert('', 0, text='Issuer Security Domain')
        self.tvi_elf = self.treeveiw_apps.insert('', 1, text='Excutable Load Files')
        self.tvi_app = self.treeveiw_apps.insert('', 2, text='Applications')
        self.treeveiw_apps.grid(column=0, row=4, columnspan=3)
        self.button_auth = ttk.Button(self.frame_app, text='Get Status...'
                                      , command=self.click_getstatus)
        self.button_auth.grid(column=0, row=5, columnspan=3)

    def click_reset(self):
        """Click a reset button
        """
        try:
            self.connector.select_reader(self.str_reader_name.get())
            self.connector.reset()
            self.gp = GP(self.connector)
        except Exception:
            tkmb.showinfo('Error', 'Please check a card or readers...')

    def click_send(self):
        """Click a send button
        """
        self.connector.send_command(self.entry_cmd.get())

    def click_exit(self):
        """Click a exit menu
        """
        self.root.quit()
        self.root.destroy()
        exit()

    def click_auth(self):
        """Click a exit menu
        """
        try:
            result, sw1, sw2 = self.gp.mutual_auth(enc=toBytes(self.entry_enc.get())
                                                   , mac=toBytes(self.entry_mac.get())
                                                   , dek=toBytes(self.entry_dek.get())
                                                   , rule=self.sv_rule.get())
            if not result:
                tkmb.showinfo('Error', 'mutual auth error...')
        except NotImplementedError:
            tkmb.showinfo('Error', 'mutual auth error...')
        except RuntimeError:
            tkmb.showinfo('Error', 'mutual auth error...')
        except Exception:
            tkmb.showinfo('Error', 'Please check a card or readers...')
            return

    def click_about(self):
        """Click a abount menu
        """
        tkmb.showinfo('About', 'About...')

    def click_getstatus(self):
        """Click a reset button
        """
        for i in self.treeveiw_apps.get_children():
            self.treeveiw_apps.delete(i)
        self.tvi_isd = self.treeveiw_apps.insert('', 0, text='Issuer Security Domain')
        self.tvi_elf = self.treeveiw_apps.insert('', 1, text='Excutable Load Files')
        self.tvi_app = self.treeveiw_apps.insert('', 2, text='Applications')
        try:
            result, sw1, sw2 = self.gp.mutual_auth(enc=toBytes(self.entry_enc.get())
                                                   , mac=toBytes(self.entry_mac.get())
                                                   , dek=toBytes(self.entry_dek.get())
                                                   , rule=self.sv_rule.get())
            if not result:
                tkmb.showinfo('Error', 'mutual auth error...')
                return
            #GET STATUS Command
            gs_apdu = GetStatus([0x80, 0xF2, 0x80, 0x00, 0x02, 0x4F, 0x00])
            response, sw1, sw2 = self.connector.send_apdu(gs_apdu)
            if sw1 == 0x90 and sw2 == 0x00:
                data = gs_apdu.parse_response()
                self.treeveiw_apps.insert(self.tvi_isd, 0, text=toHexString(data[0][0])
                                          , values=('{:02X}'.format(data[0][1])
                                          , '{:02X}'.format(data[0][2])))
            gs_apdu = GetStatus([0x80, 0xF2, 0x20, 0x00, 0x02, 0x4F, 0x00])
            response, sw1, sw2 = self.connector.send_apdu(gs_apdu)
            if sw1 == 0x90 and sw2 == 0x00:
                data = gs_apdu.parse_response()
                for x in range(len(data)):
                    self.treeveiw_apps.insert(self.tvi_elf, 0, text=toHexString(data[x][0])
                                              , values=('{:02X}'.format(data[x][1])
                                              , '{:02X}'.format(data[x][2])))
            gs_apdu = GetStatus([0x80, 0xF2, 0x24, 0x00, 0x02, 0x4F, 0x00])
            response, sw1, sw2 = self.connector.send_apdu(gs_apdu)
            if sw1 == 0x90 and sw2 == 0x00:
                data = gs_apdu.parse_response()
                for x in range(len(data)):
                    self.treeveiw_apps.insert(self.tvi_app, 0, text=toHexString(data[x][0])
                                              , values=('{:02X}'.format(data[x][1])
                                              , '{:02X}'.format(data[x][2])))
        except NotImplementedError:
            tkmb.showinfo('Error', 'mutual auth error...')
            return
        except RuntimeError:
            tkmb.showinfo('Error', 'mutual auth error...')
            return
        except Exception:
            tkmb.showinfo('Error', 'Please check a card or readers...')
            return


class DebuggerWidget(object):
    """Debugger class
    """

    def __init__(self):
        """Construct a new Debugger.
        """
        self.__printer = None

    def set_debug_widget(self, widget):
        """Sets a tkinter widget for printing a log.
        It recommends that the widget is an instance of the Entry widget.
        """
        self.__printer = widget

    def print_log(self, str_log_message):
        """Prints a log message
        """
        if self.__printer is not None:
            self.__printer.insert(tk.END, str_log_message)
            self.__printer.see(tk.END)
        print(str_log_message)


class SCComponent(object):
    """SCComponent class
    It is a base class of the ''scm'' module.
    """

    def __init__(self, debugger):
        """Construct a new SCComponent.
        """
        self.debugger = debugger

    def print_log(self, str_log_message):
        """Prints a log message
        """
        self.debugger.print_log(str_log_message)


class Connector(SCComponent):
    """Connector class
    """

    def __init__(self, debugger):
        """Construct a new Connector.
        """
        super().__init__(debugger)
        self.refresh()
        self._selected_reader = None
        self._connection = None

    def get_all_connectors(self):
        """Returns the list of all smartcard connectors'' names.

        Returns:
            The name list of all smaartcard connectors.
        """
        # n = len(self._readers)
        # names = []
        # for i in range(n):
        #     names.append(self._readers[i].name)
        
        names = [name.name for name in self._readers]
        return names

    def get_selected_connector_name(self):
        """Returns the name of a selected connector.

        Returns:
            the name of a selected connector.
        """
        return self._selected_reader.name

    def refresh(self):
        """Refresh the list of smartcard connectors.
        """
        self._readers = readers()

    def select_reader(self, str_connector_name):
        """Sets a selected connector

        Args:
            str_connector_name (str) -- the name of a selected connector.

        Raises:
            ValueError -- The ''str_connector_name'' value is invalid.
        """
        b_found = False
        for r in self._readers:
            if r.name == str_connector_name:
                self._selected_reader = r
                b_found = True
                break
        if not b_found:
            raise ValueError

    def reset(self):
        """Reset a card in a selected connector

        Returns:
            The ATR(Answer to Reset) of a card.

        Raises:
            IOError -- the card does not connected to a selected connector.
        """
        if self._selected_reader is None:
            raise IOError
        if self._connection is not None:
            self._connection.disconnect()
            self._connection = None
        self._connection = self._selected_reader.createConnection()
        self._connection.connect()
        self.print_log('ATR: ' + self.get_atr() + '\n')
        return self.get_atr()

    def get_atr(self):
        """Returns a ATR(Answer to Reset) of a card.

        Returns:
            The ATR(Answer to Reset) of a card.
        """
        return toHexString(self._connection.getATR())

    def send_command(self, apdu):
        """Sends a apdu command to a smartcard.
        """
        if type(apdu) == str:
            #buf_apdu = CommandAPDU(apdu).toBytes()
            buf_apdu = toBytes(apdu)
        elif type(apdu) == list:
            buf_apdu = apdu
        response, sw1, sw2 = self._connection.transmit(buf_apdu)
        capdu = '< ' + toHexString(buf_apdu) + '\n'
        rapdu = ('> ' + toHexString(response) + '\n> {:02X}'.format(sw1)
                 + ' {:02X}'.format(sw2) +'\n')
        self.print_log(capdu)
        self.print_log(rapdu)
        if sw1 == 0x61:        # Get Response
            get_response = '00C00000' + '{:02X}'.format(sw2)
            buf_apdu = toBytes(get_response)
            response, sw1, sw2 = self._connection.transmit(buf_apdu)
            capdu = '< ' + toHexString(buf_apdu) + '\n'
            rapdu = ('> ' + toHexString(response) + '\n> {:02X}'.format(sw1)
                     + ' {:02X}'.format(sw2) +'\n')
            self.print_log(capdu)
            self.print_log(rapdu)
        return response, sw1, sw2

    def send_apdu(self, apdu):
        """Sends a apdu command to a smartcard.

        Args:
            apdu -- APDU instance
        """
        response, sw1, sw2 = self.send_command(apdu.get_apdu())
        apdu.response(response, sw1, sw2)
        return response, sw1, sw2