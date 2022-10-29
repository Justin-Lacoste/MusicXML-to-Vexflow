//import vexflow in html file

async function create_vexflow(canvas_id, start_measure, end_measure, json_data_filename) {


	const user_tempo = "tempo"
	const pro_tempo = "pro_tempo"
	const user_intensity = "graph_played_velocity"//"intensity"
	const pro_intensity = "graph_pro_velocity"
	function merge_song_array_to_vexflow_data(song_array, vexflow_data, mode, start_measure, end_measure, recorded_start_measure, recorded_end_measure) {
		var color_type = ""
		if (mode == "tempo_graph")
			color_type = "tempo_color"
		if (mode == "intensity_graph")
			color_type = "intensity_color"
		for (var i=recorded_start_measure;i<=recorded_end_measure;i++) {
			var measure = vexflow_data[i]
			for (var voice_number of Object.keys(measure)) {
				for (var j=0;j<measure[voice_number].length;j++) {
					if ('song_array_index' in measure[voice_number][j] && measure[voice_number][j]["song_array_index"] != -1) {
						if (mode == "tempo_graph" || mode == "intensity_graph") {
							measure[voice_number][j][mode] = song_array[measure[voice_number][j]["song_array_index"]][color_type]
						}
						if (mode == "feedback") {
							measure[voice_number][j]["highlight"] = song_array[measure[voice_number][j]["song_array_index"]]["highlight"]
						}
						measure[voice_number][j]["user_tempo"] = song_array[measure[voice_number][j]["song_array_index"]][user_tempo]
						measure[voice_number][j]["pro_tempo"] = song_array[measure[voice_number][j]["song_array_index"]][pro_tempo]
						measure[voice_number][j]["user_intensity"] = song_array[measure[voice_number][j]["song_array_index"]][user_intensity]
						measure[voice_number][j]["pro_intensity"] = song_array[measure[voice_number][j]["song_array_index"]][pro_intensity]
					}
				}
			}
		}
	}

	function mode_to_color(mode) {
		const mode_to_color_map = {"-2": '#0526FF', "-1": "#031380", "0": "#000000", "1": "#800303", "2": "#FF0505"}
		return mode_to_color_map[mode]
	}
	no_color_note = '#D8D8D8'


	//for testing
	const total_with = 1112
	const height_of_stave = 41


	var previous_x_position = 25
	var added_height_for_second_stave = 100
	var previous_y_position = (window.innerHeight-(2*height_of_stave+added_height_for_second_stave))/2;

	//Setting up context and renderer
 	const { Renderer, Stave, StaveNote, Voice, Formatter, StaveConnector, Dot, Accidental, GhostNote, Beam, StaveTie, Curve } = Vex.Flow;
	const div = document.getElementById(canvas_id);
	const renderer = new Renderer(div, Renderer.Backends.SVG);
	renderer.resize(window.innerWidth,  window.innerHeight); //renderer.resize(1500, 1500);   
	const context = renderer.getContext();


	function dotted(note) {
	  Dot.buildAndAttach([note]);
	  return note;
	}
	//Loading data
	try {
		var data = await fetch(json_data_filename).then(response => {return response.json()})
	}
	catch(err) {
		alert("Server error: ", err)
	}

	var measures = data.measures

	var note_ids = []

	for (var measure_number=start_measure; measure_number<end_measure+1; measure_number++) {

		var measure = measures[measure_number]

		//LAYOUT
		var width_of_stave =Math.round(measure["layout"]["measure_width"])*(window.innerWidth/total_with) //Math.round(measure["layout"]["measure_width"])
		var row_start = measure["layout"]["row_start"]
		//console.log(row_start)


		// Create a stave : Stave(x_position, y_position, width_of_stave)
		const stave1 = new Stave(previous_x_position, previous_y_position, width_of_stave);
		if (row_start)
			stave1.addClef("treble").addTimeSignature("6/4");
		const stave2 = new Stave(previous_x_position, previous_y_position+added_height_for_second_stave, width_of_stave);
		if (row_start)
			stave2.addClef("bass").addTimeSignature("6/4");
		previous_x_position += width_of_stave
		


		var voices = []
		var voices_with_stave = []
		var beams = []
		var notes_per_voice = {}


		for (var voice_number of Object.keys(measure)) {


			if (voice_number.includes("beam") == false && voice_number.includes("slurs_and_ties") == false && voice_number.includes("layout") == false) {

				var vexflow_notes = []
				
				var notes = []

				var notes_for_debug = []

				var stave_number;

				for (let i=0;i<measure[voice_number].length;i++) {

					//NOTES
					var note = measure[voice_number][i]
					var note_dict = { keys: note["notes"], duration: note["duration"]}

					if (note["staff"] == "2") {
						note_dict["clef"] = "bass"
						stave_number = 2
					}
					else {
						stave_number = 1
					}


					//STEM DIRECTION
					if (note["stem"] == 1 || note["stem"] == -1) {
					note_dict["stem_direction"] = note["stem"]
					}


					//CREATE NOTE
					var note_vexflow;
					if (note["ghost"]) {
						note_dict["keys"] = ["c/4"]
						note_vexflow = new GhostNote(note_dict).setStyle({fillStyle: "rgba(0,0,0,1)", strokeStyle: "rgba(0,0,0,1)"});
					}
					else {
						note_vexflow = new StaveNote(note_dict)		
					}

					

					//ACCIDENTALS
					for (let j=0;j<note["accidentals"].length;j++) {
						var accidental = note["accidentals"][j]["accidental"]
						var index_accidental = note["accidentals"][j]["index"]
						note_vexflow.addModifier(new Accidental(accidental), index_accidental)
					}

					//DOT
					if (note["dotted"]) {
						note_vexflow = dotted(note_vexflow)
					}

					notes.push(note_vexflow)
					if (note["is_played"])
						note_ids.push(note_vexflow.attrs.id) //For the graph generator

					if (voice_number in notes_per_voice) {
						notes_per_voice[voice_number].push(note_vexflow)
					}
					else {
						notes_per_voice[voice_number] = [note_vexflow]
					}
					notes_for_debug.push(note_dict)
				}

				//BEAMS
				var beams_voice_name = voice_number + "_beams"
				if (beams_voice_name in measure) {
					var beams_voice = measure[beams_voice_name]
					for (var i=0;i<beams_voice.length;i++) {
						var beam_start = beams_voice[i]['begin']
						var beam_end = beams_voice[i]['end']
						var group = notes.slice(beam_start, beam_end)
						var beam = new Vex.Flow.Beam(group)
						beam.maintain_stem_directions = true
						beams.push(beam)
					}
				}

				//voice
				const voice = new Voice({ num_beats: 6, beat_value: 4 });
				//console.log(notes_for_debug)
				voice.addTickables(notes);
				voices.push(voice)
				voices_with_stave.push([stave_number, voice])
			}

		}


		new Formatter().joinVoices(voices).format(voices, width_of_stave-20);
		stave1.setContext(context).draw();
		stave2.setContext(context).draw();


		//console.log(stave1)	
		
		for (var i=0;i<voices_with_stave.length;i++) {
			var voice = voices_with_stave[i][1]
			var stave_number = voices_with_stave[i][0]
			if (stave_number == 1) {
				voice.draw(context, stave1)
			}
			else {

				voice.draw(context, stave2)
			}
		}


		//BEAMS
		for (var i=0;i<beams.length;i++) {
			beams[i].setContext(context).draw()
		}


		//TIES AND CURVES
		var ties = []
		var curves = []
		for (var i=0;i<measure["slurs_and_ties"].length;i++) {

			var tie_info = measure["slurs_and_ties"][i]

			if (tie_info["type"] == "done") {

				if (tie_info["start_placement"] != "above") { 

					var tie_dict = {
						first_note: notes_per_voice[tie_info["start_voice"]][tie_info["start_bucket_number"]],
						last_note: notes_per_voice[tie_info["end_voice"]][tie_info["end_bucket_number"]],
						first_indices: [tie_info["start_note_rank"]],
						last_indices: [tie_info["end_note_rank"]],
					}
					var tie = new StaveTie(tie_dict)
					ties.push(tie)
				}
				else {

					var curve_dict = {
						position: Curve.Position.NEAR_TOP,
						position_end: Curve.Position.NEAR_TOP,
						invert: true,
					   	x_shift: -4,
					   	y_shift: 5,
					   	thickness: 1.5,
					}
					var first_note = notes_per_voice[tie_info["start_voice"]][tie_info["start_bucket_number"]]
					var last_note = notes_per_voice[tie_info["end_voice"]][tie_info["end_bucket_number"]]
					var curve = new Curve(first_note, last_note, curve_dict)
					curves.push(curve)


				}
			}
		}

		ties.forEach((t) => {
		  t.setContext(context).draw();
		});
		curves.forEach((c) => {
		  c.setContext(context).draw();
		});
		console.log("d")


		if (row_start) {
			const connector = new StaveConnector(stave1, stave2)
        	.setType('brace')
			connector.setContext(context).draw();
		}
		else {
			const connector = new StaveConnector(stave1, stave2)
        	.setType('single')
			connector.setContext(context).draw();
		}

	}
}