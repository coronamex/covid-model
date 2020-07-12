params.base_de_datos = "../datos/datos_abiertos/base_de_datos.csv.gz"
params.lut_estados = "../datos/util/estados_lut_datos_abiertos.csv"
ENTIDADES = Channel.of(1..32)

process modelo_mexico{
  tag "$entidad"
  cpus 4
  conda "/opt/modules/pkgs/anaconda/4.8/envs/sur"
  publishDir "R_efectiva/entidades",
    mode: 'rellink',
    pattern: "r_efectiva.csv",
    saveAs: {"r_efectiva_${entidad}.csv"}

  input:
  val entidad from ENTIDADES
  val base_de_datos from params.base_de_datos
  val lut_estados from params.lut_estados

  output:
  file 'r_efectiva.csv'

  """
  ${workflow.projectDir}/modelo_mexico.py \
    --base_de_datos $base_de_datos \
    --lut_estados $lut_estados \
    --region $entidad
  """
}
