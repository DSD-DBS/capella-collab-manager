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

   Additionally, you have to adjust the styles in `src/styles.css`
3) Add the file `src/environments/environment.prod.ts` with the following content: 
    ```
    export const environment = {
        production: false,
        backend_url: '/api/v1',
        privacy_statement: 'https://example.com/privacy',
        imprint: 'https://example.com/imprint',
    };
    ```
4) 
    ```
    docker build -t t4c/client/frontend .
    ```

## Run it

```
docker run -p 8000:80 t4c/client/frontend
```
