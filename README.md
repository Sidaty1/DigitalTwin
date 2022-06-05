TODO

    -> Regler le problem de src dans les unittests OK 
    -> Faire un Readme: 
            -> Structure du projet 
                -> SRC: chaque classe et sa fonction 
                -> Scenes: faire des examples 
                        -> Skeletonization 
                        -> ...etc
                -> Unittest: 
                        -> Montrer des screenshots 
                -> Validation: Explication de la solution manufacturée utilisée et présenter les résultats
                -> Data 
            -> Comment lancer le digital twin 
                -> Choisir les parametres dans parameters.py: expliquer chaque parametre 
                -> Chmod +x du fichier bash 
                -> Lancer le bash: expliquer ces étapes 
            -> TODO: 
                -> Add a Meshlab module to process vessel mehes before skeletonization
                -> Une loi de comportement plus complexe provenant de Sonics 
                -> Une methode de frontière emergée: PhiFEM 
                -> choisir les bons parametres 
                -> les bonnes conditions limites
    -> Validation avec solution manufacturée: possible ? 
    -> Push le code sur Gitlab

# Liver Digital Twin 

This project automates the generation of the liver digital twin given input parenchyma and vessels meshes. 

The pipeline is as follows: 

Add here figure of parenchyma and vessels in parallel and the mapping to join both models 




## Installation


```bash
git clone ...
```


## Usage

```python
import foobar

# returns 'words'
foobar.pluralize('word')

# returns 'geese'
foobar.pluralize('goose')

# returns 'phenomenon'
foobar.singularize('phenomena')
```


## Tests 



## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)