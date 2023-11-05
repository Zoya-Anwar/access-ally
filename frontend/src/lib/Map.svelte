<!-- Map.svelte -->

<script>
  import { onMount } from 'svelte';
  let map;

  // Use dynamic import to load Leaflet
  onMount(() => {
    import('leaflet').then((L) => {
      // Create the map
      map = L.map('map').setView([54.166363, -4.482263], 13);

      // Add a tile layer (you'll need to replace the tile URL)
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      }).addTo(map);

      // Add a path using the coordinates from your JSON data
      const coordinates = [[54.166363, -4.482263], [54.1668, -4.482847], ...]; // Add all coordinates from your JSON data

      L.polyline(coordinates, { color: 'blue' }).addTo(map);
    });
  });
</script>

<div id="map" style="height: 400px; width: 100%;"></div>

