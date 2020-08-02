library(tidyverse)

lut_zms <- read_csv("../datos/util/zonas_metropolitanas_2015.csv")
zm_pobs <- lut_zms %>%
  group_by(CVE_ZM) %>%
  summarise(pob = sum(POB_2015),
            NOM_ZM = unique(NOM_ZM)) %>%
  ungroup()
zm_pobs



selected_zms <- lut_zms %>%
  filter(CVE_ZM != "09.01") %>%
  group_by(CVE_ZM, CVE_ENT) %>%
  summarise(pob = sum(POB_2015),
            NOM_ENT = unique(NOM_ENT),
            CVE_ENT = unique(CVE_ENT),
            NOM_ZM = unique(NOM_ZM),
            CVE_ZM = unique(CVE_ZM)) %>%
  ungroup() %>%
  split(.$CVE_ZM) %>%
  map_dfr(function(d){
    d %>%
      mutate(pob_prop = pob / sum(pob)) %>%
      arrange(desc(pob)) %>%
      head(1)
  }) %>%
  select(-pob) %>%
  left_join(zm_pobs, by = c("CVE_ZM", "NOM_ZM")) %>%
  # print(n = 100) %>%
  split(.$CVE_ENT) %>%
  map_dfr(function(d){
    d %>%
      arrange(desc(pob)) %>%
      head(1)
  }) %>%
  # print(n = 100) %>%
  bind_rows(tibble(CVE_ZM = "09.01",
                   CVE_ENT = "09",
                   NOM_ENT = "Ciudad de México",
                   NOM_ZM = "Valle de México")) %>%
  select(-pob_prop, -pob) %>%
  print(n = 100)


lut_zms %>%
  select(CVE_ZM, NOM_ZM, CVE_MUN, NOM_MUN) %>%
  inner_join(selected_zms, by = c("CVE_ZM", "NOM_ZM")) %>%
  write_csv("selected_zms.csv")
  
 
