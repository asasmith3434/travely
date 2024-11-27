<template>
  <div ref="globeContainer" style="width: 100%; height: 500px;"></div>
</template>

<script>
import Globe from "globe.gl";
import d3 from "d3-dsv";
import indexBy from "index-array-by";

export default {
  name: "GlobeView",
  mounted() {
    const globe = Globe()(this.$refs.globeContainer)
      .globeImageUrl("//unpkg.com/three-globe/example/img/earth-night.jpg")
      .pointOfView({ lat: 37.7749, lng: -122.4194, altitude: 1 });

    // Ensure the globe is fully loaded before adding flight routes
    globe.onGlobeReady(() => {
      this.addFlightRoutes(globe);
    });
  },
  methods: {
    addFlightRoutes(globe) {
      const OPACITY = 0.3;
      const COUNTRY = 'Portugal'; // Modify as needed

      // Sample flight route data
      const flightRoutes = [
        { from: { lat: 39.9526, lng: -75.1652 }, to: { lat: 35.1495, lng: -90.0490 }, airline: 'Airline A', srcIata: 'PHL', dstIata: 'MEM' },
        { from: { lat: 35.1495, lng: -90.0490 }, to: { lat: 30.2672, lng: -97.7431 }, airline: 'Airline B', srcIata: 'MEM', dstIata: 'AUS' },
        { from: { lat: 30.2672, lng: -97.7431 }, to: { lat: 39.9526, lng: -75.1652 }, airline: 'Airline C', srcIata: 'AUS', dstIata: 'PHL' },
      ];

      // Adding the flight routes to the globe
      globe.addArcs(
        flightRoutes.map(route => ({
          startLat: route.from.lat,
          startLng: route.from.lng,
          endLat: route.to.lat,
          endLng: route.to.lng,
          arcColor: [`rgba(0, 255, 0, ${OPACITY})`, `rgba(255, 0, 0, ${OPACITY})`],
          arcDashLength: 0.4,
          arcDashGap: 0.2,
          arcDashAnimateTime: 1500,
        }))
      );

      // Load data and process flight arcs and airports
      Promise.all([
        fetch('https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat').then(res => res.text()),
        fetch('https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat').then(res => res.text())
      ]).then(([airportsData, routesData]) => {
        const airportParse = ([airportId, name, city, country, iata, icao, lat, lng]) => ({
          airportId, name, city, country, iata, icao, lat, lng
        });

        const routeParse = ([airline, airlineId, srcIata, srcAirportId, dstIata, dstAirportId, codeshare, stops, equipment]) => ({
          airline, airlineId, srcIata, srcAirportId, dstIata, dstAirportId, codeshare, stops, equipment
        });

        const parsedAirports = d3.csvParseRows(airportsData, airportParse);
        const parsedRoutes = d3.csvParseRows(routesData, routeParse);

        // Filter routes and airports based on a specific country
        const filteredAirports = parsedAirports.filter(d => d.country === COUNTRY);
        const byIata = indexBy(filteredAirports, 'iata', false);

        const filteredRoutes = parsedRoutes
          .filter(d => Object.prototype.hasOwnProperty.call(byIata, d.srcIata) && Object.prototype.hasOwnProperty.call(byIata, d.dstIata))
          .filter(d => d.stops === '0') // Non-stop flights
          .map(d => Object.assign(d, {
            srcAirport: byIata[d.srcIata],
            dstAirport: byIata[d.dstIata]
          }));

        globe
          .pointsData(filteredAirports)
          .arcsData(filteredRoutes)
          .arcLabel(d => `${d.airline}: ${d.srcIata} &#8594; ${d.dstIata}`)
          .arcStartLat(d => d.srcAirport.lat)
          .arcStartLng(d => d.srcAirport.lng)
          .arcEndLat(d => d.dstAirport.lat)
          .arcEndLng(d => d.dstAirport.lng)
          .arcColor(d => [`rgba(0, 255, 0, ${OPACITY})`, `rgba(255, 0, 0, ${OPACITY})`])
          .arcDashLength(0.4)
          .arcDashGap(0.2)
          .arcDashAnimateTime(1500)
          .onArcHover(hoverArc => {
            globe.arcColor(d => {
              const op = !hoverArc ? OPACITY : d === hoverArc ? 0.9 : OPACITY / 4;
              return [`rgba(0, 255, 0, ${op})`, `rgba(255, 0, 0, ${op})`];
            });
          })
          .pointOfView({ lat: 37.6, lng: -16.6, altitude: 0.4 });
      });
    }
  }
};
</script>

<style scoped>
/* Optional: Customize the globe styling */
</style>
