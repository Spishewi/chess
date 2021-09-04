import json
import time
from tkinter.constants import ANCHOR
from PIL import Image
from PIL import ImageTk
import tkinter as tk
import tkinter.ttk as ttk
import src.my_globals as my_globals

class ChessBase:
    def __init__(self, canvas, gamemode, theme, sendcommand, parent):
        self.gamemode = gamemode
        self.canvas = canvas
        self.theme = theme
        self.case_size = self.theme['theme']['case_size']
        self.socksend = sendcommand
        self.parent = parent
        self.chessboard_positions = []
        self.ismyturn = False
        self.last_clicked_case = None
        self.hightlighted_case = None
        self.pawn_mv2 = None
        
        if gamemode == None:
            self.iswhite = False
            self.parent.master.title("The opponent's turn")
        else:
            self.iswhite = True
            self.parent.master.title("Your turn")
            self.ismyturn = True

        if gamemode != None:
            gamemodes = my_globals.gamemodes
            self.socksend(f"gm{gamemodes.index(gamemode)}")
            self.draw_chessboard()
        
                

    def handle_socket_message(self, message):
        print("get :", message)
        message = str(message)
        if message.startswith("gm"):
            gamemodes = my_globals.gamemodes
            self.gamemode = gamemodes[int(message[2:])]
            self.draw_chessboard()
        elif message.startswith("mv"): # normal move
            coords = message[2:].split(";")
            print(coords)
            self.deplace(int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3]))
            if self.chessboard_positions[int(coords[2])][int(coords[3])][0].endswith("pawn") and abs(int(coords[1])-int(coords[3])) == 2 and coords[0] == coords[2]:
                self.pawn_mv2 = (int(coords[2]), int(coords[3]))
            else:
                self.pawn_mv2 = None
            self.ismyturn = True
            self.parent.master.title("Your turn")
        elif message.startswith("rm"): #handle spécials deaths
            coords = message[2:].split(";")
            self.handle_death(int(coords[0]), int(coords[1]))
        elif message.startswith("ca"): #castling
            coords = message[2:].split(";")
            print(coords)
            self.deplace(int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3]))
            


    def handle_event(self, event):
        x = int(event.x/self.case_size)
        y = int(event.y/self.case_size)
        if not self.iswhite:
            x = abs(x-7)
            y = abs(y-7)
        
        deplaced = False
        self.hightlight_case(x, y)
        if self.iswhite:
            team = "white"
        else:
            team = "black"
        if self.last_clicked_case != None:
            if self.chessboard_positions[self.last_clicked_case[0]][self.last_clicked_case[1]] != None:
                if self.chessboard_positions[self.last_clicked_case[0]][self.last_clicked_case[1]][0].startswith(team):
                    if self.chessboard_positions[x][y] == None or not self.chessboard_positions[x][y][0].startswith(team):
                        if self.ismyturn:
                            if self.check_move(self.last_clicked_case[0],self.last_clicked_case[1], x, y):
                                try:
                                    
                                    self.deplace(self.last_clicked_case[0],self.last_clicked_case[1], x, y, socksend=True)
                                    deplaced = True
                                    self.ismyturn = False
                                    self.parent.master.title("The opponent's turn")
                                    if self.hightlighted_case != None:
                                        self.canvas.delete(self.hightlighted_case)
                                        self.hightlighted_case = None
                                except:
                                    pass
        if deplaced:
            self.last_clicked_case = None
        else:
            self.last_clicked_case = (x, y,)
        print(f"click at ({x};{y})")

    def draw_chessboard(self):
        print("gamemode :", self.gamemode)
        self.load_images()
        for i in range(0, 8):
            for j in range(0, 8):
                if i%2 == 0:
                    if j%2 == 0:
                        self.canvas.create_rectangle(i*self.case_size, j*self.case_size,i*self.case_size+self.case_size, j*self.case_size+self.case_size, fill=self.theme['theme']['white'], width=0)
                    else:
                        self.canvas.create_rectangle(i*self.case_size, j*self.case_size,i*self.case_size+self.case_size, j*self.case_size+self.case_size, fill=self.theme['theme']['black'], width=0)
                else:
                    if j%2 == 0:
                        self.canvas.create_rectangle(i*self.case_size, j*self.case_size,i*self.case_size+self.case_size, j*self.case_size+self.case_size, fill=self.theme['theme']['black'], width=0)
                    else:
                        self.canvas.create_rectangle(i*self.case_size, j*self.case_size,i*self.case_size+self.case_size, j*self.case_size+self.case_size, fill=self.theme['theme']['white'], width=0)
        for i in range(8):
            tmp = []
            for j in range(8):
                tmp.append(None)
            self.chessboard_positions.append(tmp)
        self.place_all()
        fill_color = self.theme["theme"]["hightlight_color"]
        fill_color = int(fill_color[1:3],16),int(fill_color[3:5],16),int(fill_color[5:7],16)
        fill_color = fill_color + (int(float(self.theme["theme"]["hightlight_alpha"])*255),)

        rect = Image.new('RGBA', (self.case_size, self.case_size), fill_color)

        self.hightlight_image = ImageTk.PhotoImage(rect)

        self.canvas.bind("<Button>", self.handle_event)
        
    def load_images(self):
        self.sprites = {}
        sprites = my_globals.chessmen
        for sprite in sprites:
            with Image.open(f"theme/img/{sprite}.png") as image:
                x = image.getbbox()[2]
                y = image.getbbox()[3]

                if x > y:
                    newx = int(round((self.case_size/10*9)))
                    newy = int(round(y/x*(self.case_size/10*9)))
                else:
                    newx = int(round(x/y*(self.case_size/10*9)))
                    newy = int(round((self.case_size/10*9)))

                self.sprites[sprite] = ImageTk.PhotoImage(image=image.resize((newx, newy,)))
        #print(self.sprites)
        
    def place(self, sprite, x, y, tags=[]):
        if self.chessboard_positions[x][y] != None:
            self.handle_death(x, y)
        if not self.iswhite:
            posx = round(self.case_size*abs(x-7)+self.case_size/2)
            posy = round(self.case_size*abs(y-7)+self.case_size/2)
        else:
            posx = round(self.case_size*x+self.case_size/2)
            posy = round(self.case_size*y+self.case_size/2)

        self.chessboard_positions[x][y] = (sprite, self.canvas.create_image(posx, posy, image=self.sprites[sprite]), tags,)

    def deplace(self, oldx, oldy, newx, newy, socksend=False):
        sprite = self.chessboard_positions[oldx][oldy][0]
        tags = self.chessboard_positions[oldx][oldy][2]
        self.canvas.delete(self.chessboard_positions[oldx][oldy][1])
        self.chessboard_positions[oldx][oldy] = None
        if "never_moved" in tags:
            tags.remove("never_moved")
        self.place(sprite, newx, newy, tags=tags)
        if socksend:
            self.socksend(f"mv{oldx};{oldy};{newx};{newy}")

    def handle_death(self, x, y):
        print(f"{self.chessboard_positions[x][y][0]} in ({x};{y}) dead.")
        self.canvas.delete(self.chessboard_positions[x][y][1])
        self.chessboard_positions[x][y] = None

    def place_all(self):
        self.place("black_rook", 0, 0, tags=["never_moved"])
        self.place("black_knight", 1, 0, tags=["never_moved"])
        self.place("black_bishop", 2, 0, tags=["never_moved"])
        self.place("black_queen", 3, 0, tags=["never_moved"])
        self.place("black_king", 4, 0, tags=["never_moved"])
        self.place("black_bishop", 5, 0, tags=["never_moved"])
        self.place("black_knight", 6, 0, tags=["never_moved"])
        self.place("black_rook", 7, 0, tags=["never_moved"])
        for i in range(8):
            self.place("black_pawn", i, 1, tags=["never_moved"])

        self.place("white_rook", 0, 7, tags=["never_moved"])
        self.place("white_knight", 1, 7, tags=["never_moved"])
        self.place("white_bishop", 2, 7, tags=["never_moved"])
        self.place("white_queen", 3, 7, tags=["never_moved"])
        self.place("white_king", 4, 7, tags=["never_moved"])
        self.place("white_bishop", 5, 7, tags=["never_moved"])
        self.place("white_knight", 6, 7, tags=["never_moved"])
        self.place("white_rook", 7, 7, tags=["never_moved"])
        for i in range(8):
            self.place("white_pawn", i, 6, tags=["never_moved"])

        for i in self.chessboard_positions:
            for j in i:
                if j == None:
                    print(f"{j};", end="")
                else:
                    print(f"{j[0]};", end="")
            print()

    def hightlight_case(self, x, y):
        if self.hightlighted_case != None:
            self.canvas.delete(self.hightlighted_case)
            self.hightlighted_case = None

        if not self.iswhite:
            oldx = abs(x-7)
            oldy = abs(y-7)
        else:
            oldx = x
            oldy = y

        self.hightlighted_case = self.canvas.create_image(oldx*self.case_size, oldy*self.case_size, image=self.hightlight_image, anchor=tk.NW)
        
        if self.chessboard_positions[x][y] != None:
            self.canvas.tag_raise(self.chessboard_positions[x][y][1])
    
    def check_move(self, oldx, oldy, newx, newy, for_casteling=False):
        chessman = self.chessboard_positions[oldx][oldy][0]
        print(chessman)
        print(self.pawn_mv2)
        if chessman.endswith("rook"):
            if oldx == newx:
                if oldy < newy:
                    for i in range(oldy+1, newy):
                        if self.chessboard_positions[oldx][i] != None:
                            return False
                elif oldy > newy:
                    for i in range(newy+1, oldy):
                        if self.chessboard_positions[oldx][i] != None:
                            return False
            elif oldy == newy:
                if oldx < newx:
                    for i in range(oldx+1, newx):
                        if self.chessboard_positions[i][oldy] != None:
                            return False
                elif oldx > newx:
                    for i in range(newx+1, oldx):
                        if self.chessboard_positions[i][oldy] != None:
                            return False
            else:
                return False
            return True
        elif chessman.endswith("king"):
            if not for_casteling and self.check_for_castling(oldx, oldy, newx, newy):
                return True
            elif abs(oldx - newx) <= 1 and abs(oldy - newy) <= 1:
                return True
            else:
                return False
        elif chessman.endswith("bishop"):
            if abs(oldx - newx) == abs(oldy - newy):
                if oldx < newx:
                    if oldy < newy:
                        for x in range(oldx+1, newx):
                            for y in range (oldy+1, newy):
                                if oldx-x == oldy-y:
                                    if self.chessboard_positions[x][y] != None:
                                        return False
                    else:
                        for x in range(oldx+1, newx):
                            for y in range (newy+1, oldy):
                                if oldx-x == y-oldy:
                                    if self.chessboard_positions[x][y] != None:
                                        return False
                else:
                    if oldy < newy:
                        for x in range(newx+1, oldx):
                            for y in range (oldy+1, newy):
                                if x-oldx == oldy-y:
                                    if self.chessboard_positions[x][y] != None:
                                        return False
                    else:
                        for x in range(newx+1, oldx):
                            for y in range (newy+1, oldy):
                                if x-oldx == y-oldy:
                                    if self.chessboard_positions[x][y] != None:
                                            return False
                return True
            else:
                return False
        elif chessman.endswith("queen"):
            if abs(oldx - newx) == abs(oldy - newy) or oldx == newx or oldy == newy:
                if oldx == newx:
                    if oldy < newy:
                        for i in range(oldy+1, newy):
                            if self.chessboard_positions[oldx][i] != None:
                                
                                return False
                    elif oldy > newy:
                        for i in range(newy+1, oldy):
                            if self.chessboard_positions[oldx][i] != None:
                                return False
                elif oldy == newy:
                    if oldx < newx:
                        for i in range(oldx+1, newx):
                            if self.chessboard_positions[i][oldy] != None:
                                return False
                    elif oldx > newx:
                        for i in range(newx+1, oldx):
                            if self.chessboard_positions[i][oldy] != None:
                                return False
                elif abs(oldx - newx) == abs(oldy - newy):
                    if oldx < newx:
                        if oldy < newy:
                            for x in range(oldx+1, newx):
                                for y in range (oldy+1, newy):
                                    if oldx-x == oldy-y:
                                        if self.chessboard_positions[x][y] != None:
                                            print(f"({x};{y})")
                                            return False
                        else:
                            for x in range(oldx+1, newx):
                                for y in range (newy+1, oldy):
                                    if oldx-x == y-oldy:
                                        if self.chessboard_positions[x][y] != None:
                                            print(f"({x};{y})")
                                            return False
                    else:
                        if oldy < newy:
                            for x in range(newx+1, oldx):
                                for y in range (oldy+1, newy):
                                    if x-oldx == oldy-y:
                                        if self.chessboard_positions[x][y] != None:
                                            print(f"({x};{y})")
                                            return False
                        else:
                            for x in range(newx+1, oldx):
                                for y in range (newy+1, oldy):
                                    if x-oldx == y-oldy:
                                        if self.chessboard_positions[x][y] != None:
                                            print(f"({x};{y})")
                                            return False
                else:
                    return False
            else:
                return False
        elif chessman.endswith("knight"):
            if (abs(oldx-newx) == 1 and abs(oldy-newy) == 2) or (abs(oldx-newx) == 2 and abs(oldy-newy) == 1):
                return True
            else:
                return False
        elif chessman.endswith("pawn"):
            if self.iswhite:
                if oldy-newy == 1:
                    if abs(oldx-newx) == 1:
                        if self.chessboard_positions[newx][newy] != None:
                            if self.chessboard_positions[newx][newy][0].startswith("black"):
                                return True
                        elif oldy == 3 and oldx-newx == -1 and self.chessboard_positions[newx][newy+1] != None and self.pawn_mv2 != None:
                            if newx == self.pawn_mv2[0] and newy == self.pawn_mv2[1]-1:
                                self.socksend(f"rm{oldx+1};{oldy}")
                                self.handle_death(oldx+1, oldy)
                                return True
                        elif oldy == 3 and oldx-newx == 1 and self.chessboard_positions[newx][newy+1] != None and self.pawn_mv2 != None:
                            if newx == self.pawn_mv2[0] and newy == self.pawn_mv2[1]-1:
                                self.socksend(f"rm{oldx-1};{oldy}")
                                self.handle_death(oldx-1, oldy)
                                return True
                    elif oldx-newx == 0:
                        if self.chessboard_positions[newx][newy] == None:
                            return True
                elif oldy-newy == 2 and oldx-newx == 0 and oldy == 6 and self.chessboard_positions[newx][5] == None and self.chessboard_positions[newx][4] == None:
                    return True
                       
            else:
                if oldy-newy == -1:
                    if abs(oldx-newx) == 1:
                        if self.chessboard_positions[newx][newy] != None:
                            if self.chessboard_positions[newx][newy][0].startswith("white"):
                                return True
                        elif oldy == 4 and oldx-newx == -1 and self.chessboard_positions[newx][newy-1] != None and self.pawn_mv2 != None:
                            if newx == self.pawn_mv2[0] and newy == self.pawn_mv2[1]+1:
                                self.socksend(f"rm{oldx+1};{oldy}")
                                self.handle_death(oldx+1, oldy)
                                return True
                        elif oldy == 4 and oldx-newx == 1 and self.chessboard_positions[newx][newy-1] != None and self.pawn_mv2 != None:
                            if newx == self.pawn_mv2[0] and newy == self.pawn_mv2[1]+1:
                                self.socksend(f"rm{oldx-1};{oldy}")
                                self.handle_death(oldx-1, oldy)
                                return True
                    elif oldx-newx == 0:
                        if self.chessboard_positions[newx][newy] == None:
                            return True
                elif oldy-newy == -2 and oldx-newx == 0 and oldy == 1 and self.chessboard_positions[newx][2] == None and self.chessboard_positions[newx][3] == None:
                    return True
                
            
            return False
        return True
                
    def check_for_castling(self, oldx, oldy, newx, newy):
        print("checking for casteling")
        print(self.chessboard_positions[oldx][oldy])
        if "never_moved" in self.chessboard_positions[oldx][oldy][2]: #verifier si le roi n'ai jamais bougé
            cases_to_check = []
            print("never_moved")
            if self.iswhite:
                # check si c'est un roque
                if newx == 2 and newy == 7:
                    if "never_moved" in self.chessboard_positions[0][7][2]:
                        cases_to_check = [(0, 7),(1, 7), (2, 7), (3, 7), (4, 7)]
                        rook_pos = (0, 7)
                    else:
                        return False
                elif newx == 6 and newy == 7:
                    if "never_moved" in self.chessboard_positions[7][7][2]:
                        cases_to_check = [(7, 7), (6, 7), (5, 7), (4, 7)]
                        rook_pos = (7, 7)
                    else:
                        return False
                else:
                    return False
            else:
                if newx == 2 and newy == 0:
                    #grand roque
                    if "never_moved" in self.chessboard_positions[0][0][2]:
                        cases_to_check = [(0, 0),(1, 0), (2, 0), (3, 0), (4, 0)]
                        rook_pos = (0, 0)
                    else:
                        return False
                elif newx == 6 and newy == 0:
                    if "never_moved" in self.chessboard_positions[7][0][2]:
                        cases_to_check = [(7, 0), (6, 0), (5, 0), (4, 0)]
                        rook_pos = (7, 0)
                    else:
                        return False
                else:
                    return False
            print("get cases to check")
            #si oui, get les ennemies

            """
            tmp = [j for sub in self.chessboard_positions for j in sub]
            enemy_list = []
            for i in tmp: # il me manque les coords des pions donc ça casse les couilles, changer ça
                    if i != None:
                        if self.iswhite:
                            if i[0].startswith("black"):
                                enemy_list.append((self.chessboard_positions.index(x), self.chessboard_positions.index(y),))
                        else:
                            if i[0].startswith("white"):
                                enemy_list.append((self.chessboard_positions.index(x), self.chessboard_positions.index(y),))
            print("get enemy list")
            """
            #print(json.dumps(self.chessboard_positions, indent=4, separators=(", ", ": "), sort_keys=True))
            enemy_pos_list = []
            for y in self.chessboard_positions:
                for x in y:
                    if x != None:
                        if self.iswhite:
                            if x[0].startswith("black"):
                                enemy_pos_list.append((self.chessboard_positions.index(y), y.index(x), ))
                        else:
                            if x[0].startswith("white"):
                                enemy_pos_list.append((self.chessboard_positions.index(y), y.index(x), ))
            print(enemy_pos_list)
            
            #verifier si les cases sont libres
            for case_to_check in cases_to_check:
                if case_to_check != cases_to_check[0] and case_to_check != cases_to_check[-1]:
                    if self.chessboard_positions[case_to_check[0]][case_to_check[1]] != None:
                        return False
            print("verif cases vides")

            #verifier si il y a des enemy
            for case_to_check in cases_to_check:
                print(enemy_pos_list)
                for enemy in enemy_pos_list:
                    print(enemy[0], enemy[1], case_to_check[0], case_to_check[1])
                    if self.check_move(enemy[0], enemy[1], case_to_check[0], case_to_check[1], for_casteling=True):
                        return False
            print("réussi")
            self.castling(rook_pos[0], rook_pos[1], oldx, oldy, newx, newy) #tout les roques ne vont pas fonctionner, corriger ça 
                                                                            #(la tour vas pas tj là ou il u avais le roi)
            self.socksend(f"ca{rook_pos[0]};{rook_pos[1]};{oldx};{oldy}")
            return True
        return False
    def castling(self, rookx, rooky, kingx, kingy, newkingx, newkingy):
        self.deplace(kingx, kingy, newkingx, newkingy)
        self.deplace(rookx, rooky, kingx, kingy)
        

            

        







