# coding: utf-8
import os, subprocess, shlex, re, platform, sys, logging, shutil
from datetime import datetime
from os import path

try: input = raw_input
except NameError: pass

class Backup:
    def __init__(self):
        self.target = ""
        self.name   = ""
        self.fs     = ""
        self.actions= []
        self.size   = 0
        self.log    = ""
        self.err    = ""
        self.custom = ""
        
        now = datetime.now()
        now = now.strftime("%Y-%m-%d_%H-%M-%S")
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        file_handler = logging.FileHandler('logique_'+now+'.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    @staticmethod
    def validate_path(prompt):
        while True:
            path_str = input(prompt)
            path_str = '/Volumes/'+path_str.strip()
            if path.exists(path_str):
                print("OK")
                return path_str
            else:
                print("Erreur : le chemin n'existe pas")
                print(path_str)

    @staticmethod
    def validate_fs(prompt):
        while True:
            fs_str = input(prompt)
            fs_str = fs_str.strip().lower()
            if fs_str in ["a", "apfs"]:
                print("OK : APFS")
                return "APFS"
            elif fs_str in ["h", "hfs+"]:
                print("OK : HFS+")
                return "HFS+"
            else:
                print("Erreur : option invalide")

    def setup(self):
        questions = {
            "target": "Volume de destination /Volumes/? :",
            "name": "Nom du conteneur DMG sans extension :",
            "fs": "Système de fichier (A)PFS ou (H)FS+ :",
        }
        self.target = self.validate_path(questions["target"])
        while True:
            q_name = input(questions["name"])
            fname = f"{self.target}/{q_name}.dmg"
            print(fname)
            if not path.exists(fname):
                print("OK")
                self.name = q_name
                break
            else:
                print("Erreur : le fichier existe")
        self.fs = self.validate_fs(questions["fs"])


    def custom_path(self):
        while self.act_q("Ajouter un autre dossier à copier ? ", "N"):
            while True:
                q_custom = input("Chemin : ").rstrip()
                if path.exists(q_custom):
                    print("OK")
                    self.custom = q_custom
                    return True
                else:
                    print("Erreur : chemin non trouvé")
        return False


    def actions_setup(self):
        actions = []
        if self.act_q("Copie de /Users"):
            actions.append("US")
        if self.act_q("Copie de /private"):
            actions.append("PR")
        if self.act_q("Copie de /Library"):
            actions.append("LI")
        if self.act_q("Copie de " + self.fseventsd()):
            actions.append("FE")
        if self.act_q("Copie de /Applications", "N"):
            actions.append("AF")
        if self.act_q("Liste des applications"):
            actions.append("AP")
        if self.custom_path():
            actions.append("CP")
    
        self.actions = actions
    
    @staticmethod
    def act_q(question, default="O"):
        while True:
            q = input(question + " (O/n) :" if default == "O" else question + " (o/N) :")
            q_lower = q.lower()
            if q_lower == "o" or (default == "O" and q == ""):
                print("Ok: " + question)
                return True
            elif q_lower == "n" or (default == "N" and q == ""):
                return False
            else:
                print("Erreur: option invalide")

    def get_copy_size(self):
        size = 0
        if 'US' in self.actions :
            size += self.get_size_b("/Users")
        if 'PR' in self.actions :
            size += self.get_size_b("/private")
        if 'LI' in self.actions :
            size += self.get_size_b("/Library")
        if 'FE' in self.actions :
            size += self.get_size_b(self.fseventsd())
        if 'AF' in self.actions :
            size += self.get_size_b("/Applications")
        if 'CP' in self.actions :
            size += self.get_size_b(self.custom)
        min_size = 3*1024*1024
        size = int(round(size * 1.2))
        if size < (5*1024*1024):
            size += min_size
        self.size = size

    def batch_copy(self):
        if 'FE' in self.actions:
            os.mkdir('/Volumes/'+self.name+'/fseventsd/')
            self.rsync(self.fseventsd(), '/Volumes/'+self.name+'/fseventsd/')
        if 'US' in self.actions:
            self.rsync('/Users', '/Volumes/'+self.name)
        if 'PR' in self.actions:
            self.rsync('/private', '/Volumes/'+self.name)
        if 'LI' in self.actions:
            self.rsync('/Library', '/Volumes/'+self.name)
        if 'AF' in self.actions:
            self.rsync('/Applications', '/Volumes/'+self.name)
        if 'CP' in self.actions:
            self.rsync(self.custom, '/Volumes/'+self.name)
        if 'AP' in self.actions:
            self.listAp()

    @staticmethod
    def fseventsd():
        if not path.exists('/System/Volumes/Data/.fseventsd'):
            return "/.fseventsd"
        else:
            return "/System/Volumes/Data/.fseventsd"

    @staticmethod
    def sudo():
        if os.geteuid() != 0:
            return 1
        return 0

    @staticmethod
    def arch():
        if platform.machine() == "x86_64":
            return 1
        else:
            return 2

    def rsync(self, source, rtarget):
        arch = "irsync" if self.arch() == 1 else "arsync"
        command = f"./bin/{arch} -XEva --inplace {source} {rtarget}"
        print(f"Copie de {source} vers {rtarget}...")
        process = subprocess.run(shlex.split(command),
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True)
        stdout = process.stdout
        stderr = process.stderr
        self.logger.info(f"RSYNC:{source}\n{stdout}")
        if stderr:
            self.logger.error(f"RSYNC:{source}\n{stderr}")


    @staticmethod
    def get_size(folder):
        pattern = '[0-9]*'
        stream = os.popen('du -s '+folder)
        text = stream.read()
        res = re.search(pattern, text)
        return int(res.group(0))*512

    def get_size_b(self, source):
        arch = "irsync" if self.arch() == 1 else "arsync"
        args = f'-XEvan {source} /tmp 2>/dev/null | grep -E "total size is [0-9,]+" -o | tr -d "," | grep -o -E "[0-9]+"'
        command = f"./bin/{arch} {args}"
        
        process = subprocess.Popen(command,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True)
        stdout, stderr = process.communicate()
        
        try:
            size = int(stdout.strip())
        except ValueError:
            size = 0
        
        print(f'{source}: {self.human_readable(size)}o')
        
        return size
    
    
    def shasum(self):
        print("Calcul du hash SHA-1 du conteneur...")
        dmg = self.target+'/'+self.name+'.dmg'
        stream = os.popen('shasum -b -a 1 '+dmg)
        text = stream.read()
        self.logger.info("HASH:\n"+text)
    

    @staticmethod
    def human_readable(total_size_in_bytes):
        if total_size_in_bytes > 1024000000:
            totalsize =  str(round(total_size_in_bytes / 1024 ** 3, 3))+"G"
        elif total_size_in_bytes > 1024000:
            totalsize = str(round(total_size_in_bytes/ 1024 ** 2, 3))+"M"
        elif total_size_in_bytes > 1024:
            totalsize = str(round(total_size_in_bytes / 1024, 3))+"K"
        else:
            totalsize = str(total_size_in_bytes)
        return totalsize
        
    def rsync_version(self):
        arch = "irsync" if self.arch() == 1 else "arsync"
        command = './bin/'+arch+' --version | grep version'
        stream = os.popen(command)
        text = stream.read()
        print(text)
        self.logger.info(text)
        
    def listAp(self):
        command = 'ls -FalT /Applications'
        stream = os.popen(command)
        text = stream.read()
        print("Liste des applications")
        f = open('/Volumes/'+self.name+'/applications.txt', 'w')
        f.write(text)
        f.close()

    def listUsers(self):
        command = 'dscacheutil -q user'
        stream = os.popen(command)
        text = stream.read()
        print("Liste des utilisateurs")
        f = open('/Volumes/'+self.name+'/utilisateurs.txt', 'w')
        f.write(text)
        f.close()
        
    def create_dmg(self):
        command = 'hdiutil create -size '+str(self.size)+' -layout NONE -type UDIF -fs '+self.fs+' -volname '+self.name+' '+self.target+'/'+self.name+'.dmg'
        args = shlex.split(command)
        print("Création du conteneur DMG. Veuillez patienter...")
        p = subprocess.Popen(args,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if not stderr :
            return 1

    def free_space(self):
        statvfs = os.statvfs(self.target)
        block_size = statvfs.f_frsize
        free_blocks = statvfs.f_bfree
        free = block_size * free_blocks
        return int(free)
    
    def check_space(self):
        free = self.free_space()
        if free <= self.size:
            print("Espace insuffisant sur la destination")
            sys.exit(1)
        else:
            print("Espace disponnible : "+str(free)+" / "+self.human_readable(free)+"o")
            return True

    def mount_dmg(self):
        dmg = self.target+'/'+self.name+'.dmg'
        command = 'hdiutil attach -noautoopen '+dmg
        args = shlex.split(command)
        print("Montage du conteneur")
        p = subprocess.Popen(args,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if path.exists('/Volumes/'+self.name+'/') :
            print("Conservation des droits...")
            scom = os.popen('vsdbutil -a /Volumes/'+self.name)
            owners = scom.read()
            return 1
    
    def fin(self):
        print("Syncing...")
        scom = os.popen('sync')
        sync = scom.read()
        print("Démontage du conteneur")
        command = 'hdiutil detach /Volumes/'+self.name
        args = shlex.split(command)
        p = subprocess.Popen(args,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        stdout = stdout.decode("utf-8")
        stderr = stderr.decode("utf-8")
        self.logger.info("FIN:\n"+stdout)
        if stderr != '':
            self.logger.error("FIN:\n"+stderr)
        
    def resume(self):
        if self.arch() == 1:
            print("Plate-forme : intel x86 64bits")
        else:
            print("Plate-forme : Apple ARM")
        print("Destination : "+self.target)
        print("Nom : "+self.name)
        print("FS : "+self.fs)
        print(self.actions)
        if 'CP' in self.actions:
            print("Autre chemin à copier : "+self.custom)
        print("Taille du conteneur : "+str(self.size)+" / "+self.human_readable(self.size)+"o")

def main():
    b = Backup()
    b.setup()
    b.actions_setup()
    b.get_copy_size()
    b.resume()
    b.check_space()
    
    dmg = b.create_dmg()
    if dmg == 1:
        print("Conteneur créé avec succès !")
        mnt = b.mount_dmg()
        if mnt == 1:
            print("Montage fait !")
            b.rsync_version()
            b.batch_copy()
            b.listUsers()
            b.fin()
            b.shasum()
            print("Fin de la copie")

if __name__ == '__main__':
    if Backup.sudo() == 0:
        os.system('clear')
        main()
    else:
        print("Droits d'administration nécessaires pour une copie efficace")
        print("Certains fichiers ne pourront être copiés.")
        print("Les infos de propriétaire GID et UID ne seront pas conservées.")
        input("Ctrl+C pour annuler - Entrée pour continuer")
        os.system('clear')
        main()

