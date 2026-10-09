ADB MASTER CONTROL v2.0 ELITE
<p align="center"> <img src="https://img.shields.io/badge/Version-2.0%20ELITE-00d084?style=for-the-badge" alt="Version"> <img src="https://img.shields.io/badge/Python-3.8+-388bfd?style=for-the-badge&logo=python&logoColor=white" alt="Python"> <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-bc8cff?style=for-the-badge" alt="Platform"> <img src="https://img.shields.io/badge/License-MIT-e3b341?style=for-the-badge" alt="License"> </p><p align="center"> <b>Interface graphique tout-en-un pour contrôler n'importe quel appareil Android via ADB.</b><br> 13 modules • Terminal intégré • Moniteur temps réel • Automatisation • Sans root requis (pour la majorité des fonctions) </p><p align="center"> <b>Auteur :</b> ML • <a href="https://github.com/exploit4040">github.com/exploit4040</a> </p>

Table des matières

    Aperçu

    Fonctionnalités

    Prérequis

    Installation

    Utilisation

    Modules détaillés

    Exemples de cas d'usage

    Dépannage

    Avertissement légal

    Licence

Aperçu

ADB MASTER CONTROL est une application de bureau Python qui centralise plus de 200 commandes ADB dans une interface graphique moderne et intuitive. Elle remplace la ligne de commande fastidieuse par des boutons clairs, tout en gardant un terminal intégré pour les utilisateurs avancés.

Conçu pour :

    Techniciens & réparateurs - diagnostics rapides, déblocage, nettoyage

    Utilisateurs avancés - personnalisation, optimisation gaming/batterie

    Pentesters & chercheurs - audit d'appareils, analyse de packages

    Apprenants - découvrir ADB sans mémoriser chaque commande

Fonctionnalités
13 modules complets
Module	Description
Dashboard	Vue d'ensemble : modèle, Android, batterie, CPU + actions rapides
Système	Redémarrages, paramètres, props, nettoyage
Hardware	Luminosité, volume, batterie, écran, touches, rafraîchissement
Réseau	WiFi, données mobiles, Bluetooth, hotspot, ping custom
Applications	Lister, désinstaller, désactiver, extraire APK, bloatware
Google Play Services	Activer/Désactiver GPS, restaurer permissions, audit
Sécurité	Verrouillage, localisation, permissions, audit ports
Options Développeur	USB debug, animations, logcat, setprop
Données & Stockage	Push/Pull fichiers, explorateur, espace disque
Personnalisation	Thèmes, DPI, polices, presets (Night/Gaming/Privacy...)
Automatisation	Scripts pré-faits, macro builder, séquences sauvegardables
Moniteur Live	Graphique batterie temps réel (Matplotlib)
Terminal ADB	Shell intégré avec historique et raccourcis
Points forts

    Auto-installation des dépendances Python (customtkinter, matplotlib)

    Interface dark moderne avec thème vert (CustomTkinter)

    Multi-thread - aucune interface figée pendant les commandes

    Journal d'activité horodaté + fichier log persistant

    Fusion de 3 anciens scripts (disable_google_play_services, enable_google_play_services, parametreopp)

    Sans root pour 95 % des fonctions (via --user 0)

    Cross-platform : Windows, Linux, macOS

Prérequis
1. Python 3.8 ou supérieur
bash

python --version

2. ADB (Android Platform Tools)

Windows - Télécharger Platform Tools
Puis ajouter le dossier au PATH.

Linux
bash

sudo apt install adb android-tools-adb

macOS
bash

brew install android-platform-tools

Vérifier l'installation :
bash

adb --version

3. Dépendances Python

Elles sont auto-installées au premier lancement, mais vous pouvez les installer manuellement :
bash

pip install customtkinter matplotlib

4. Sur le téléphone Android

    Paramètres → À propos du téléphone

    Taper 7 fois sur Numéro de build → Options développeur activées

    Options développeur → Débogage USB → Activer

    Brancher le câble USB

    Sur le téléphone : Autoriser le débogage USB pour cet ordinateur

Installation
Option 1 - Cloner le dépôt
bash

git clone https://github.com/exploit4040/adb-master-control.git
cd adb-master-control
python adb_master_control.py

Option 2 - Télécharger directement

    Télécharger adb_master_control.py

    Lancer :

bash

python adb_master_control.py

Au premier lancement, les dépendances manquantes seront installées automatiquement.
Utilisation
bash

python adb_master_control.py

L'application :

    Vérifie qu'ADB est installé

    Se connecte automatiquement au premier appareil détecté

    Affiche le Dashboard avec les infos de l'appareil

Navigation

    Sidebar gauche : cliquez sur un module pour changer de page

    Badge de connexion en haut : vert = connecté, rouge = déconnecté

    Bouton "Connecter / Rafraîchir" : relance la détection ADB

Terminal ADB intégré

Tapez directement vos commandes :
text

adb> shell getprop ro.product.model
adb> devices
adb> pull /sdcard/photo.jpg ./
adb> shell pm list packages -3

Raccourcis disponibles :

    ↑ / ↓ → historique des commandes

    help → afficher l'aide

    clear ou cls → effacer l'écran

    Boutons de raccourcis prédéfinis sous le terminal

Modules détaillés
<details> <summary><b>Google Play Services (module phare)</b></summary>

Permet de désactiver complètement Google Play Services pour :

    Économiser la batterie

    Réduire le tracking Google

    Libérer de l'espace

    Améliorer les performances

Méthodes tentées automatiquement :

    pm disable-user --user 0 com.google.android.gms

    pm disable com.google.android.gms

    cmd package disable-user --user 0 com.google.android.gms

Conséquences : Play Store inaccessible, Gmail/Maps/Drive cassés, notifications push stoppées, synchronisation désactivée.

Inclut : bouton de restauration des permissions + bouton pour tout réactiver.
</details><details> <summary><b>Gestionnaire d'applications</b></summary>

    Lister toutes / user / système / désactivées

    Filtrer par recherche

    Désinstaller, désactiver, activer, forcer l'arrêt

    Vider cache/données, extraire l'APK, voir permissions

    Bloatware killer : Facebook, Instagram, TikTok, Twitter/X, LinkedIn, Netflix en un clic

</details><details> <summary><b>Automatisation</b></summary>

Scripts prédéfinis :

    Nettoyage complet

    Optimisation gaming

    Économie batterie

    Confidentialité maximale

    Boost performances

    Mode photo/vidéo

    Reset réseau

    Mode développeur

Macro Builder : écrivez vos propres séquences de commandes (une par ligne), sauvegardez-les en .txt, rechargez-les plus tard.
</details><details> <summary><b>Moniteur temps réel</b></summary>

    Graphique batterie en direct (Matplotlib)

    Rafraîchissement configurable (5s → 2min)

    Suivi température, statut charge, uptime

    Export CSV des données collectées

</details>
Exemples de cas d'usage
Technicien réparateur

    Débloquer un téléphone, extraire les photos du client, désinstaller du bloatware, réinitialiser les réglages.

Optimisation gaming

    Preset "Gaming Mode" → animations coupées, 120Hz forcé, cache vidé, apps en arrière-plan tuées.

Audit de sécurité

    Lister les ports ouverts, vérifier les permissions, identifier les apps ayant accès à la localisation, contrôler les admins appareils.

Récupération de données

    Push/Pull de fichiers, extraction d'APK, exploration du système de fichiers, backup des contacts.

Dépannage
Problème	Solution
ADB non trouvé	Installer Platform Tools et l'ajouter au PATH
Aucun appareil connecté	Activer Débogage USB + autoriser le PC sur le téléphone
unauthorized	Débrancher/rebrancher, accepter la popup sur le téléphone
device offline	adb kill-server && adb start-server
Interface figée	Vérifier qu'une commande n'est pas bloquée (timeout 15s)
Permission denied	Certaines commandes nécessitent root
Le téléphone redémarre en boucle après désactivation GPS	Démarrer en mode recovery, activer USB debug, utiliser le bouton "Activer GPS"

Raccourci diagnostic rapide :
bash

adb kill-server
adb start-server
adb devices

Avertissement légal

    Cet outil est destiné à un usage éducatif et à l'administration d'appareils que vous possédez ou pour lesquels vous disposez d'une autorisation explicite.

        N'utilisez PAS cet outil sur un appareil qui ne vous appartient pas

        La désactivation de services système peut rendre un appareil instable

        L'auteur décline toute responsabilité en cas de dommage matériel, perte de données ou utilisation abusive

        Certaines fonctions (extraction, désinstallation système) peuvent nécessiter les droits root

        Testez toujours sur un appareil de test avant la production

Licence

Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails.
Contact

    GitHub : @exploit4040

Learn. Break. Fix. Automate. Repeat.

