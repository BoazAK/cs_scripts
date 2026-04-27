#!/bin/bash

# Définition des outils à utiliser
TOOLS=("nmap" "dirb" "nikto" "dnsrecon" "sublist3r" "crtsh" "whatweb" "wafw00f" "dnsenum" "theHarvester" "sslscan" "testssl.sh")

# Fonction pour vérifier si les outils sont installés
verifier_outils() {
  for tool in "${TOOLS[@]}"; do
    if ! command -v $tool &> /dev/null; then
      echo "L'outil $tool n'est pas installé. Veuillez l'installer pour que le script puisse fonctionner correctement."
      exit 1
    fi
  done
}

# Fonction pour demander le nom de domaine
demande_domaine() {
  read -p "Entrez le nom de domaine : " domaine
  echo "Domaine : $domaine"
}

# Fonction pour lancer les outils de reconnaissance
lancer_outils() {
  for tool in "${TOOLS[@]}"; do
    case $tool in
      nmap)
        echo "Lancement de nmap..."
        nmap -sT -O -p 1-65535 $1 > $2/nmap_$1.txt
        ;;
      dirb)
        echo "Lancement de dirb..."
        dirb http://$1 > $2/dirb_$1.txt
        ;;
      nikto)
        echo "Lancement de nikto..."
        nikto -h http://$1 > $2/nikto_$1.txt
        ;;
      dnsrecon)
        echo "Lancement de dnsrecon..."
        dnsrecon -d $1 > $2/dnsrecon_$1.txt
        ;;
      sublist3r)
        echo "Lancement de sublist3r..."
        sublist3r -d $1 > $2/sublist3r_$1.txt
        ;;
      crtsh)
        echo "Lancement de crt.sh..."
        curl -s "https://crt.sh/?q=%25.$1" | \
        grep -oP '>\K[^<]+(?=</a>)' | sort -u > $2/crtsh_$1.txt
        ;;
      whatweb)
        echo "Lancement de whatweb..."
        whatweb http://$1 > $2/whatweb_$1.txt
        ;;
      wafw00f)
        echo "Lancement de wafw00f..."
        wafw00f http://$1 > $2/wafw00f_$1.txt
        ;;
      dnsenum)
        echo "Lancement de dnsenum..."
        dnsenum $1 > $2/dnsenum_$1.txt
        ;;
      theHarvester)
        echo "Lancement de theHarvester..."
        theHarvester -d $1 -b all > $2/theHarvester_$1.txt
        ;;
      sslscan)
        echo "Lancement de sslscan..."
        sslscan --connect $1:443 > $2/sslscan_$1.txt
        ;;
      testssl.sh)
        echo "Lancement de testssl.sh..."
        testssl.sh -t $1 > $2/testssl_$1.txt
        ;;
    esac
  done
}

# Fonction pour chercher les sous-domaines valides
chercher_sous_domaines() {
  echo "Lancement de crt.sh pour chercher les sous-domaines..."
  curl -s "https://crt.sh/?q=%25.$1" | \
  grep -oP '>\K[^<]+(?=</a>)' | sort -u > $2/sous_domaines_$1.txt
  echo "Sous-domaines valides enregistrés dans $2/sous_domaines_$1.txt"
}

# Fonction pour lancer les scans sur les sous-domaines valides
lancer_scans_sous_domaines() {
  sous_domaines=$(cat $2/sous_domaines_$1.txt)
  for sous_domaine in $sous_domaines; do
    echo "Lancement des scans sur $sous_domaine..."
    lancer_outils $sous_domaine $2
  done
}

# Vérification des outils
verifier_outils

# Boucle principale
while true; do
  demande_domaine
  date=$(date +"%Y-%m-%d_%H-%M-%S")
  dossier_scan="$date_$domaine"
  mkdir $dossier_scan
  chercher_sous_domaines $domaine $dossier_scan
```bash
  read -p "Voulez-vous lancer les scans sur les sous-domaines valides ? (o/n) " reponse
  if [ "$reponse" = "o" ]; then
    lancer_scans_sous_domaines $domaine $dossier_scan
  fi
  lancer_outils $domaine $dossier_scan
  read -p "Voulez-vous continuer ? (o/n) " reponse
  if [ "$reponse" != "o" ]; then
    break
  fi
done