# Samling 1  
## Felles prosjekt: Dataanalytiker + Anvendt maskinlæring

Dere skal jobbe i tverrfaglige grupper (Dataanalytiker og Anvendt maskinlæring) og løse en felles case.

**High level beskrivelse:**
![alt text](image.png)

**Eksempl på agent work flow:**
![alt text](image-1.png)
## Oppgavebeskrivelse
Fagskolen Viken ønsker et KI-basert program som har kunnskap om alle studiene de tilbyr. Programmet skal kunne:
- svare på spørsmål om studietilbud og innhold (for nyansatte og veiledere)
- støtte potensielle studenter i å finne riktig studie basert på behov og interesser

Primærkilden skal være informasjonen som ligger på fagskolens nettsider. I tillegg ønsker fagskolen at løsningen senere kan utvides med andre kilder, for eksempel:
- studentprosjekter
- artikler/blogg
- faglærerressurser og interne dokumenter

## Overordnede krav

- hente og strukturere studieinformasjon fra nettsiden
- lagre informasjonen i en database (strukturert og søkbar)
- tilby tilgang til data via en MCP-server
- bruke en multi-agent-tilnærming for å hente, bearbeide og presentere informasjon til brukeren

## Oppgaven består av

### 1) Innhenting og strukturering av data
- Hent studieinformasjon fra:  
  [Studier – Fagskolen Viken](https://fagskolen-viken.no/studier?f%5B0%5D=apent_for_opptak%3A1)
- Filtrer og rens data (f.eks. fjerne støy, standardisere tekst og felter)
- Lagre data i database
- Test og verifiser at data er korrekt lagret

**Informasjon dere skal forsøke å lagre (så langt det finnes på nettsiden):**
- Hovedtekst / beskrivelse av studiet
- Studiepoeng
- Undervisningsspråk
- Nivå
- Hvorfor velge dette studiet?
- Hva lærer du?
- Undervisning og samlinger
- Obligatorisk oppmøte
- Politiattest (der det finnes)
- Karrieremuligheter
- “Har du noen spørsmål?” / kontaktinfo (der det finnes)
- Lenke til hvert studie

**Informasjon om emner (der det finnes og er tilgjengelig):**
- Lenke til hvert emne i studiet
- Studiepoeng
- Studienivå
- Læringsutbytte:
  - Kunnskap
  - Ferdigheter
  - Generell kompetanse

### 2) Database
- Design en database med tabeller som representerer studie informasjon på en ryddig måte
- Implementer og fyll databasen med data fra nettsiden
- Test at data kan hentes ut igjen på en fornuftig måte (f.eks. ved enkle spørringer/verifikasjon)

### 3) MCP-server
- Bygg en MCP-server som gir tilgang til data i databasen
- Lag en løsning der data kan hentes ut på en strukturert måte via MCP

### 4) Multi-agent
- Design en multi-agent-løsning som bruker MCP-serveren til å hente data
- Agentene skal samarbeide om å finne relevant informasjon og formulere svar til brukeren
- Agentenes ansvar og samarbeid skal beskrives kort (hva de gjør og hvorfor)

# Gjennomføring

## KI i prosjektet
I prosjektet skal dere bruke KI aktivt både til læring og problemløsning: idéutvikling, teknisk design, koding, dokumentasjon og feilsøking.

**Regler for KI-bruk:**
- Maks 10 prompts per time per gruppe
- Hver prompt skal godkjennes av veileder 

## Læringsark
Hver gruppe skal fylle ut en A3 ark for hver dag om hva dere har lært. Arket skal innehode stikkord med korte forklaringer. For eks.

- **Agent verktøy**: et verktøy en LLM agent har tilgang til, for eks. sanntids vær data. 


## Arbeidsform
Dere skal jobbe agilt og iterativt. Målet er å få en fungerende helhet tidlig og forbedre gjennom flere runder.

**Typisk iterasjon:** 
design → implementer → test → vurder forbedringer → redesign


---

# Innlevering
Hver gruppe leverer ett Git-repo som inneholder:

- **Kildekode** (scraping/innhenting, database, MCP-server, agent-løsning)
- **Databaseoppsett** SQL-skript for database
- **Kjørbarhet**: README med
  - hvordan sette opp miljø
  - hvordan kjøre innhenting og fylle DB
  - hvordan starte MCP-server
  - hvordan kjøre/demo agentløsningen
- **Eksempler:** screenshot av chat som viser funksjonalitet. 