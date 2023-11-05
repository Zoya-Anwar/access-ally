<script>
   import LoadingIndicator from './Loading.svelte';


   /**
    * @type string
    */
   export let pathwidth;
   /**
    * @type Array<string>
    */
   export let pathincline;
   /**
    * @type Array<string>
    */

   export let timelight;
   /**
    * @type Array<string>
    */

   export let paved;
   /**
    * @type Array<string>
    */
   export let selectedCategories;
   /**
    * @type string
    */
   export let specificDescriptors;
   /**
    * @type Boolean
    */
   export let loading;

  let userLocation = '';

  async function getLocation() {
    try {
      const position = await navigator.geolocation.getCurrentPosition();
      const { latitude, longitude } = position.coords;
      userLocation = `Latitude: ${latitude}, Longitude: ${longitude}`;
    } catch (error) {
      userLocation = '-4.4824, 54.1663';
    }
  }

  let sliderValue = 50;

   let pathwidths = [
      { value: 0.7, title: 'No aid-700mm' },
      { value: 0.75, title: 'Walking Stick-750mm' },
      { value: 0.9, title: '2 Walking Sticks/Crutches/Walking Frame-900mm' },
	  { value: 1.2, title: 'Visually Impaired and using a cane/or with a Guide dog-1200mm'},
	  { value: 1.5, title: 'Wheelchair-1500mm' },

   ];

   let pathinclines = [
      { value: 12, title: 'Wheelchair-1:12' },
      { value: 20, title: 'Buggy-1:20' },
   ];

   let timelights = [
      { value: 'DayM', title: 'Morning' },
      { value: 'AfterN', title: 'Afternoon' },
      { value: 'Night', title: 'Night' },
	  { value: 'NotSel', title: 'Rather not choose' },
   ];

   let paveds = [
      { value: 'Yes', title: 'Yes' },
      { value: 'No', title: 'No' },
   ];
</script>

<div class="pt-6 md:pt-10 text-slate-200">
   <div>
	   <div class="mb-8">
         <div class="mb-4 font-semibold text-lg">What is your start location?</div>
         <div class="flex items-center">
			<input type="text" class="mb-4 font-semibold text-lg rounded-full border" style="margin-right: 10px; font-family: 'Arial Black'" bind:value={userLocation} readonly />
            <br>
			<button class="mb-4 font-semibold text-lg" on:click={getLocation}>Get Location</button>
         </div>
      </div>

	   <div class="mb-8">
         <div class="mb-4 font-semibold text-lg">What distance would you like to travel?</div>
         <div class="flex items-center">
			<input type="range" bind:value={sliderValue} min="0" max="10000" step="1" style="margin-right: 10px; margin-bottom: 10px" />
			<div class="mb-4 font-semibold text-lg">Distance: {sliderValue} metres</div>
         </div>
      </div>

      <div class="mb-8">
         <div class="mb-4 font-semibold text-lg">What kind of path width do you require?</div>
         <div class="flex items-center">
            {#each pathwidths as type (type.value)}
               <button
                  on:click={() => {
                     pathwidth = type.value;
                  }}
                  class={`${
                     pathwidth === type.value ? 'bg-green-600/40' : ''
                  } text-slate-200 font-bold mr-2 text-sm mt-2 py-2 px-4 rounded-full border border-green-600`}
               >
                  {type.title}
               </button>
            {/each}
         </div>
      </div>
	   <div class="mb-8">
         <div class="mb-4 font-semibold text-lg">What kind of path incline would you prefer?</div>
         <div class="flex items-center">
            {#each pathinclines as type (type.value)}
               <button
                  on:click={() => {
                     pathincline = type.value;
                  }}
                  class={`${
                     pathincline === type.value ? 'bg-green-600/40' : ''
                  } text-slate-200 font-bold mr-2 text-sm mt-2 py-2 px-4 rounded-full border border-green-600`}
               >
                  {type.title}
               </button>
            {/each}
         </div>
      </div>
	   <div class="mb-8">
         <div class="mb-4 font-semibold text-lg">Do you require a paved path??</div>
         <div class="flex items-center">
            {#each paveds as type (type.value)}
               <button
                  on:click={() => {
                     paved = type.value;
                  }}
                  class={`${
                     paved === type.value ? 'bg-green-600/40' : ''
                  } text-slate-200 font-bold mr-2 text-sm mt-2 py-2 px-4 rounded-full border border-green-600`}
               >
                  {type.title}
               </button>
            {/each}
         </div>
      </div>
	   <div class="mb-8">
         <div class="mb-4 font-semibold text-lg">What time will you be walking?</div>
         <div class="flex items-center">
            {#each timelights as type (type.value)}
               <button
                  on:click={() => {
                     timelight = type.value;
                  }}
                  class={`${
                     timelight === type.value ? 'bg-green-600/40' : ''
                  } text-slate-200 font-bold mr-2 text-sm mt-2 py-2 px-4 rounded-full border border-green-600`}
               >
                  {type.title}
               </button>
            {/each}
         </div>
      </div>
      <div class="mt-8">
         <div class="mb-4 font-semibold text-lg">
            Ask our AI assistant Ally for any other specifications. Be as picky as you'd like.
         </div>
         <textarea
            bind:value={specificDescriptors}
            class="bg-white/40 border border-white/0 p-2 rounded-md placeholder:text-slate-800 text-slate-900 w-full h-20 font-medium"
            placeholder="Ex. Must have at least 2 seasons and be on Netflix or Hulu."
         />
         <button
            on:click
            class={`${
               loading
                  ? 'bg-green-400/50'
                  : 'bg-green-600 hover:bg-gradient-to-r from-green-700 via-green-600 to-green-700 '
            } mt-4 w-full h-10 text-white font-bold p-3 rounded-full flex items-center justify-center`}
         >
            {#if loading}
               <LoadingIndicator />
            {:else}
               <p>Curate My List</p>
            {/if}
         </button>
      </div>
   </div>
</div>
