# Chiedi all'utente se vuole esportare le immagini Docker
read -p "Build application? (S/N): " build_app
read -p "Vuoi esportare l'immagine Docker? (S/N): " export_images
read -p "Specifica il tag per le immagini Docker (latest/stable): " docker_tag

# Converte la risposta in maiuscolo per una corretta gestione
export_images=$(echo "$export_images" | tr '[:lower:]' '[:upper:]')
build_app=$(echo "$build_app" | tr '[:lower:]' '[:upper:]')

# Verifica se il tag è valido
if [[ "$docker_tag" != "latest" && "$docker_tag" != "stable" ]]; then
  echo "Tag non valido. Usa 'latest' o 'stable'."
  exit 1
fi

if [ "$build_app" == "S" ]; then
  echo "Start building application"
  docker image rm moellhausen_prompt_designer:"$docker_tag"
  docker buildx build --force-rm --no-cache -t moellhausen_prompt_designer:"$docker_tag" .
  echo "End building application"
  if [ "$export_images" == "S" ]; then
    echo "Start export application"
    docker save -o moellhausen_prompt_designer_"$docker_tag".tar moellhausen_prompt_designer:"$docker_tag"
    echo "End Export application"
  fi
fi