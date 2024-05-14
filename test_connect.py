import socket

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
    valeur_battery = data.decode(encoding="utf-8")
    if valeur_battery == "ok":
        return 0
    else:
        return valeur_battery.replace("\r\n", "")

retour = do_command ("command")
print(f"Retour de 'command': {retour}")
etat_batterie = do_command ("battery?")
print(f"Retour de 'battery?': {etat_batterie}")

sock_cmd.close()