import time

class Game:
    def __init__(self, server):
        self.server=server

    def handle_socket_state(self, socket, text):
        player=self.server.connections[socket]
        match player.state:
            case "connected":
                self.handle_connected(player, text)
            case "account_creation":
                self.handle_account_creation(player, text)
            case "account_password_creation":
                self.handle_account_password_creation(player, text)
            case "account_password_confirmation":
                self.handle_account_password_confirmation(player, text)
            case "account_login":
                self.handle_account_login(player, text)
            case "account_auth":
                self.handle_account_auth(player, text)
            case "career_select":
                self.handle_career_select(player, text)
            case "logged_in":
                self.handle_commands(player, text)

    def handle_connected(self, player, text):
        text=str(text.strip())[2:len(str(text.strip()))-1].split(" ")[0]
        match text:
            case "create":
                player.send("Enter the name of your new account\nSpaces will be replaced with dashes.\n\te.g. `Jim Bob Jo` would be replaced by `Jim-Bob-Jo`.\n")
                player.state="account_creation"
            case "login":
                player.send("enter your username\n")
                player.state="account_login"

    def handle_account_creation(self, player, text):
        text=str(text.strip())[2:len(str(text.strip()))-1].replace(" ", "-")
        player.name=text
        player.send(f"Your name will be {player.name}.\n\nEnter your password - (Note: at the moment passwords are not encrypted, please use a password you do not use else where. Encryption will be coming soon.)\n")
        player.state="account_password_creation"


    def handle_account_password_creation(self, player, text):
        text=str(text.strip())[2:len(str(text.strip()))-1]
        player.password=text
        player.send("reenter your password\n")
        player.state="account_password_confirmation"

    def handle_account_password_confirmation(self, player, text):
        text=str(text.strip())[2:len(str(text.strip()))-1]
        if player.password==text:
            player.send("Password matched. \n\n\nSelect a career from the following options:\n\t\tpioneer \t\t the founders of galactic civilisations\n\t\tpolitition \t\t The foundation of civilisations and holding their citizens in order\n\t\tpilot \t\t The members of a galatic civilisation's navy, flying ships in combat and in trade\n\t\tsoldier \t\t The members of a galatic civilisation's army, fighting in ground combat and scouting on recon mitions. \n\t\tengineer \t\t The backbone of any civilisation, building new technologies and developing those already in place\n\t\tcitizen \t\t An indevidual that travels the galaxy alone, living under any civilisation\n\n")
            player.state="career_select"


    def handle_career_select(self, player, text):
        text=str(text.strip())[2:len(str(text.strip()))-1].split(" ")[0]
        careers = ['pioneer', 'politition', 'pilot', 'soldier', 'engineer', 'citizen']
        if text in careers:
            player.career = text
            player.send(f"you are a {text}\n\n")
            self.server.db_cursor.execute(f"SELECT * FROM accounts")
            rows=self.server.db_cursor.fetchall()
            for row in rows:
                if row[0]==player.name or row[3]==player.address[0]:
                    player.send("This account already exists... \n")
                    player.disconnect()
                    return
            sql = f"INSERT INTO accounts(name,password,immortle_character,address,career) VALUES('{player.name}','{player.password}',{player.immortle_character},'{player.address[0]}','{player.career}');"
            self.server.db_cursor.execute(sql)
            self.server.db.commit()
            player.state="logged_in"
            player.send(f"you are now logged in as {player.name}\n\n")

        else:
            player.send("that's not a valid career type\n\n");

    def handle_account_login(self, player, text):
        text=str(text.strip())[2:len(str(text.strip()))-1].replace(" ", "-")
        self.server.db_cursor.execute(f"SELECT * FROM accounts WHERE name='{text}';")
        rows = self.server.db_cursor.fetchall()
        if len(rows)<1:
            player.send("this account doesn't exist, try create instead\n")
            player.state="connected"
            return
        player.send("account found\nEnter your password\n")
        player.name=text
        player.state="account_auth"

    def handle_account_auth(self, player, text):
        text=str(text.strip())[2:len(str(text.strip()))-1]
        self.server.db_cursor.execute(f"SELECT * FROM accounts WHERE name='{player.name}';")
        rows=self.server.db_cursor.fetchall()[0]
        if text==rows[1]:
            player.send("logging in\n")
            player.state="logged_in"
            player.send("logged in\n\n")
            return
        player.send("password is incorrect\n")
        player.disconnect()

    def handle_commands(self, player, text):
        text=str(text.strip())[2:len(str(text.strip()))-1].split(" ")
        match text[0]:
            case "@who":
                who_msg="\t\tOnline Players\n"
                for i in self.server.connections:
                    conn = self.server.connections[i]
                    if conn.state!="logged_in":
                        continue
                    if conn.immortle_character:
                        who_msg=who_msg+f"\t{conn.name} (immortal)\n"
                    else:
                        who_msg=who_msg+f"\t{conn.name}\n"
                who_msg=f"{who_msg}\n--------------------\n\n"
                player.send(who_msg)
            case "@ooc":
                if not len(text)>=2:
                    player.send("You need to send an actual message, duh")
                else:
                    chat=" ".join(text[1:])
                    self.server.send(f"[OOC] {player.name}: {chat}\n")
            case "@quit":
                player.send("You disconnect")
                player.disconnect()
            case other:
                player.send("invalid command")

