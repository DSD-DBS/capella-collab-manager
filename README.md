# Frontend T4C Manager

## Development

Run 
```
ng serve --open
```

## Build it

1) Place a file `logo.svg` in the folder `assets`
2) Adjust the theme colors in the file `src/custom-theme.scss`. 
   The themes can be generated here: http://mcg.mbitson.com/
3) 
    ```
    docker build -t t4c/client/frontend .
    ```

## Run it

```
docker run -p 8000:80 t4c/client/frontend
```
