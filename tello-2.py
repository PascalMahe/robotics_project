import socket, time
from time import sleep

wifi_name = "TELLO-95599"

# Pour envoyer des commandes au drone
host = '192.168.10.2'
port_cmd = 8891
locaddr_cmd = (host, port_cmd)
sock_cmd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address_cmd = ('192.168.10.1', 8889)
sock_cmd.bind(locaddr_cmd)

def do_command (cmd) :
    # Envoyer la commande
    sock_cmd.sendto(cmd.encode(encoding="utf-8"), tello_address_cmd)
    data, server = sock_cmd.recvfrom(1518)
    # Récupérer l'information de la batterie
    # print(data)
    valeur_battery = data.decode(encoding="latin-1")
    if valeur_battery == "ok":
        return 0
    else:
        return valeur_battery.replace("\r\n", "")


# Programmation du drone
retour = do_command ("command")
print(f"Retour de 'command': {retour}")
retour = do_command ("takeoff")
print(f"Retour de 'takeoff': {retour}")
etat_batterie = do_command ("battery?")
print(f"Retour de 'battery?': {etat_batterie}")
# print(etat_batterie)
# retour = do_command("up 60")
# print(f"Retour de 'up 60': {retour}")
# retour = do_command("cw 180")
# print(f"Retour de 'cw 180': {retour}")
# retour = do_command("down 60")
# print(f"Retour de 'down 60': {retour}")
# retour = do_command("cw 180")
# print(f"Retour de 'cw 180': {retour}")
# retour = do_command("up 60")
# print(f"Retour de 'up 60': {retour}")

retour = do_command("flip f")
print(f"Retour de 'flip f': {retour}")

retour = do_command ("land")
print(f"Retour de 'land': {retour}")

sock_cmd.close()