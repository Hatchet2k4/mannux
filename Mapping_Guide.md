When creating maps for Mannux, the following guidelines should be followed:

  * Each room is 20x15 tiles in size. Large rooms should be multiple of this size.
  * The main layer is simply called Walls. This is the layer where most of the ground and walls should be drawn, and is the layer where Tabby and most entities are drawn. Obstructions should be placed on this layer. Background objects such as boxes and background walls can also go on this layer.
  * There is another layer for Doors, where the doorway tiles will go, on top of the Walls layer so Tabby appears behind them. Currently, obstructions on this layer cause the block underneath on the Walls layer to be destructible.

**Todo: cover metadata for automap system. Zones for secret areas/mapswitches**

Above all, experiment! Have fun putting different combinations of tiles together.