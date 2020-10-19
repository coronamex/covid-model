params.base_de_datos = "../datos/datos_abiertos/base_de_datos.csv.gz"
params.lut_estados = "../datos/util/estados_lut_datos_abiertos.csv"
params.lut_zms = "selected_zms.csv"
ENTIDADES = Channel.of(1..32)
ZMS = Channel.from(["01.01","02.03","03.01","04.01","05.01",
  "06.01","07.02","08.04","09.01","10.01","11.03","12.01","13.01",
  "14.01","15.02","16.02","17.02","18.01","19.01","20.01","21.01",
  "22.01","23.01","24.02","25.01","26.02","27.01","28.05","29.01",
  "30.07","31.01","32.01"])

base_de_datos = file(params.base_de_datos)
lut_estados = file(params.lut_estados)
lut_zms = file(params.lut_zms)

process modelo_mexico{
  tag "$entidad"
  cpus 4
  // conda "/opt/modules/pkgs/anaconda/4.8/envs/sur"
  publishDir "R_efectiva/entidades",
    mode: 'copy',
    pattern: "r_efectiva.csv",
    saveAs: {"r_efectiva_${entidad}.csv"}
  stageInMode 'rellink'

  input:
  val entidad from ENTIDADES
  val base_de_datos
  val lut_estados

  output:
  file 'r_efectiva.csv'

  """
  ${workflow.projectDir}/modelo_mexico.py \
    --base_de_datos $base_de_datos \
    --lut_estados $lut_estados \
    --region $entidad
  """
}

process modelo_mexico_zms{
  tag "$zm"
  cpus 4
  // conda "/opt/modules/pkgs/anaconda/4.8/envs/sur"
  publishDir "R_efectiva/zms",
    mode: 'copy',
    pattern: "r_efectiva.csv",
    saveAs: {"r_efectiva_${zm}.csv"}
  stageInMode 'rellink'

  input:
  val zm from ZMS
  val base_de_datos
  val lut_zms

  output:
  file 'r_efectiva.csv'

  """
  ${workflow.projectDir}/modelo_mexico_zms.py \
    --base_de_datos $base_de_datos \
    --lut_zms $lut_zms \
    --region $zm
  """
}
