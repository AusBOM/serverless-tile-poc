# Serverless Tile

This service generates raster tiles from a geotiff using AWS S3 and lamba.

Note:  This has never been tested in a production environment.  So please report any bugs or issues.

## Features

- No server setup required.

- Caches tiles in S3 to avoid having to regenerate them.

- Allows styling of tiles.

- On the fly styling allowed through the API call.

- Styling customisation includes colours, resampling method, use of gradient, and setting the value at which the style colours are cycled.

- Uses an Open Street Map server XYZ format.

- Easy to add new source data for tiles. (via pushing a STAC file with the location.)

- Ideal for use with COGs (Cloud Optimised Geotiffs)

- Uses rio-tiler under the hood to generate the tiles.

## How To Use

### Deployment

1. To deploy, you should first modify the `serverless.config.yaml`.  It is recommended you provide a unique name to your service.

2. Make sure you have serverless installed.  If it is not already installed you can install it with `npm install -g serverless` or a local install in the project directory.

3. Make sure you have the serverless plugins installed.
```
npm install -g serverless-python-requirements
npm install -g serverless-apigw-binary@0.4.4
```

4. Make sure have an AWS account with appropriated permissions and your credentials set in your command environment.

5. Run deploy: `sls deploy`

Keep note of the api endpoints, you will need these later.

### Adding Data

Once deployed you can send an array of STAC items (<https://github.com/radiantearth/stac-spec/tree/master/item-spec>) to the API you just deploy.

Additionally in the item-spec you need to include

- `source`: in assets the sources needs to provide a link to your data.  Accepted protocols are `https` and `s3`
- `style_indexes`: in properties takes a list of the various increments to change your styling.  At a minimum this requires the minimum and maximum values you want to use for your dataset.
- `styles`: in properties, a list of styles (the colour map for these styles will be precalculated.  It can be empty but it is recommended to have a default style.  (See adding styles below.)
Additionally it is recommended to add the `default_style` with the style id of your preferred defaults under properties.

If your data source has more than one band of data you can specify the band you want to use in properties.

An example is provided below:

```[{
  "type": "Feature",
  "id" : "UV_3hrly_AUSTR_1529971200",
  "bbox": [94.6000031, -47.4000007, 180.2000000,  -7.0000051],
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        [94.6000031,  -7.0000051],
        [94.6000031, -47.4000007],
        [180.2000000, -47.4000007],
        [180.2000000,  -7.0000051],
        [94.6000031,  -7.0000051]
      ]
    ]
  },
  "properties": {
    "datetime": "2018-06-26T00:00:0.000Z",
    "default_style": "blue-azure-aqua-blueviolet-burlywood-green-darkgreen-chartreuse-coral-darkorange-deeppink-dimgrey-darkviolet",
    "style_indexes": [0, 1, 2, 3, 4, 5, 6, 9, 12],
    "styles": [{
      "id" : "blue-aqua-burlywood-green-chartreuse-coral-darkorange-deeppink-darkviolet"
    }],
    "band": 1,
    "style_thresholds": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
  },
  "collection": "UVINDEXCS_3hrly_AUSTR",
  "links": [
  ],
  "assets": {
    "source": {
      "href": "s3://serverless-tile-test/uv.tif",
      "title": "uv",
      "product": "something" 
    }
  }
}]
```

See below about adding a style.

Send the list of STAC items, to the `/stac` endpoint you deployed earlier.
You will need to send the STAC item list as the body,  and also a header `x-api-key` with the apikey provided as output from your deployment.  Now your data is ready to use.

Note this endpoint requires an api key to prevent anyone from just adding data sources to your service.  But it may be recommended to add additional security measures.

### Using the endpoint

You can either directly hit the tile generation service or you can hit the s3 tile cache (recommended) that will automatically hit the endpoint.
To see these endpoints you can run `sls info -v` from the project directory.

If you set a default style you can now generate tiles for that data using the `/tiles/{data}/{z}/{x}/{y}` endpoint.

Where the `data` is id for your STAC item.

Alternatively you can use the `/tiles/{data}/style/{style}/{z}/{x}/{y}` where the `style` is either the id of a style specified with the STAC item or an id that can be translated to a style.  (See Below)

#### Example of use

Go to your choice of tool to display your rendered tiles.  I will use terria <https://map.terria.io> for this example.

##### Configure your data source

In terria I do this by clicking the 'Add data' button, selecting the 'My Data' tab, clicking 'Add Web Data`, selecting 'Open Street Map server' and putting in the /tiles/{data} endpoint e.g.
`http://devuser-my-serverless-tile-tile.s3-website-ap-southeast-2.amazonaws.com/tiles/UV_3hrly_AUSTR_1529971200`
or
`https://xxxxxxxxxx.execute-api.ap-southeast-2.amazonaws.com/devuser/tiles/UV_3hrly_AUSTR_1529971200`

### Adding a style

#### Style ID

The simplest way to specify a style is to use the id.

If the id is `red-green-blue`. Then is will by default transition as a gradient from red to green then to blue.  If your indexes are `[0, 10, 100]` Then values between 0 and 10 in the data will be transitions between red and green and the values between 10 and 100 would transition between green and blue.

If you wanted all values below 10 as red, between 10 and 100 as red and at 100 as blue.  You can set the id as `nogradient-red-green-blue` or alternatively set gradient with a value of `false`.

You can also set the resampling method in the id e.g. `nearest-red-green-blue` or `nogradient-nearest-red-green-blue`.

The colours specified can be either a html color name or a hexcode. e.g. `indianred-#00ff00-#0000ff`.

Alternatively you can set the colours as a list in the style, and the id will be used as alias.  (Note: If you use `default` as the id it will automatically make it the default style)

##### Style Parameters

Style takes the following parameters:

`id`: *Required* The id to identify the style and also as mentioned above can be used to set the basic styling options.
`colours`: An ordered list of the colours to use when styling tiles for this data.  If left out, it will attempt to use the id to determine the colours to use.
`gradient`: A boolean, if true colours will transition between each other on a gradient, if false will jump between colours at the style indexes.
`resampling_method`: The resampling method to use, options include:
- bilinear (default)
- nearest
- cubic
- average
`hide_min`: A boolean, if true makes all pixels equal to or below the minimum show as transparent.
`hide_max`: A boolean, if true makes all pixels equal to or above the maximum show as transparent.

## S3 Tile Cache

The deployment will automatically set you up with an s3 bucket which will populate tiles.  The ideal way to use this service is to hit the s3 endpoint under /tiles/{data}.  If the tile has been generated it will get it as a simple http request if the tile hasn't been generated the request will be redirected to the lambda function will send back the tile and populate the s3 bucket with the tile.

The s3 bucket contains a folder for each style.