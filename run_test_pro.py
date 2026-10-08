import subprocess, shutil

shutil.copyfile('KiCad_Project/WaterSensor.kicad_pro', 'KiCad_Project/test_stt17.kicad_pro')
res = subprocess.run([
    'E:/KidCad/bin/kicad-cli.exe', 'pcb', 'drc',
    '--refill-zones', 'KiCad_Project/test_stt17.kicad_pcb'
], capture_output=True, text=True)
print("DRC with matching kicad_pro:")
print(res.stdout)
