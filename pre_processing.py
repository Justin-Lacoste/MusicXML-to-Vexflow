#### INPUT ####
xml_file = ''

notes = ["empty", "la_0, la#_0", "si_0",
		"do_1", "do#_1", "re_1", "re#_1", "mi_1", "fa_1", "fa#_1", "sol_1", "sol#_1", "la_1", "la#_1", "si_1",
		"do_2", "do#_2", "re_2", "re#_2", "mi_2", "fa_2", "fa#_2", "sol_2", "sol#_2", "la_2", "la#_2", "si_2",
		"do_3", "do#_3", "re_3", "re#_3", "mi_3", "fa_3", "fa#_3", "sol_3", "sol#_3", "la_3", "la#_3", "si_3",
		"do_4", "do#_4", "re_4", "re#_4", "mi_4", "fa_4", "fa#_4", "sol_4", "sol#_4", "la_4", "la#_4", "si_4",
		"do_5", "do#_5", "re_5", "re#_5", "mi_5", "fa_5", "fa#_5", "sol_5", "sol#_5", "la_5", "la#_5", "si_5",
		"do_6", "do#_6", "re_6", "re#_6", "mi_6", "fa_6", "fa#_6", "sol_6", "sol#_6", "la_6", "la#_6", "si_6",
		"do_7", "do#_7", "re_7", "re#_7", "mi_7", "fa_7", "fa#_7", "sol_7", "sol#_7", "la_7", "la#_7", "si_7",
		"do_8"]


#CREATE LIST OF BUCKETS OF NOTES OF MUSICXML SHEET MUSIC

from xml.dom import minidom
from xml.dom.minidom import parse, parseString
import xml.etree.ElementTree as ET
import numpy as np

#TODO:
# 1. Make list of flat or sharp for a portion of the piece to apply on notes
# 2. Find way to position note in relation to the measure (with length of note, should be good enough for now,
#                                                           or the x-coordinate thing!)

letters_to_notes = {"A": "la", "B": "si", "C": "do", "D": "re", "E": "mi", "F": "fa", "G": "sol"}

musicxml_measures = []
layouts = []

divisions = -1
time_signature_numerator = -1
time_signature_denominator = -1

circle_of_fifth = [{},
                   {"fa": 1},
                   {"do": 1, "fa": 1},
                   {"do": 1, "fa": 1, "sol": 1},
                   {"do": 1, "re": 1, "fa": 1, "sol": 1},
                   {"do": 1, "re": 1, "fa": 1, "sol": 1, "la": 1},
                   {"do": -1, "re": -1, "mi": -1, "sol": -1, "la": -1, "si": -1},
                   {"re": -1, "mi": -1, "sol": -1, "la": -1, "si": -1},
                   {"re": -1, "mi": -1, "la": -1, "si": -1},
                   {"mi": -1, "la": -1, "si": -1},
                   {"mi": -1, "si": -1},
                   {"si": -1}]

modifiers = []
note_id = 0

dom = minidom.parse('Liebestraum.xml')
measures = dom.getElementsByTagName('measure')
print(f"There are {len(measures)} items:")

divisions = int(dom.getElementsByTagName('divisions')[0].childNodes[0].data)
time_signature_numerator = int(dom.getElementsByTagName('beats')[0].childNodes[0].data)
time_signature_denominator = int(dom.getElementsByTagName('beat-type')[0].childNodes[0].data)

for index, measure in enumerate(measures):
    if index < 20:

        measure_musicxml_notes = []

        measure_number = measure.attributes['number'].value
        measure = parseString(measure.toxml())

        #LAYOUT
        layout = {}
        #width
        layout["measure_width"] = measure.getElementsByTagName('measure')[0].attributes['width'].value
        #row
        if len(measure.getElementsByTagName('system-layout')) > 0:
            layout["row_start"] = True
        else:
            layout["row_start"] = False
        layouts.append(layout)

        duration = 0

        #arpeggios = {} #key: 'default-x', value: {key: 'default-y', value: timestamp}

        #check for key
        key = measure.getElementsByTagName('fifths')
        if len(key) > 0:
          key = key[0].childNodes[0].data
          print(key)
          modifiers = circle_of_fifth[int(key)]

        root = ET.fromstring(measure.toxml())

        chord_number = 0

        for child_of_measure in root:
            if child_of_measure.tag == "note":
                note_xml_string = ET.tostring(child_of_measure, encoding='unicode')

                if 'pitch' in note_xml_string:
                    note = parseString(note_xml_string)
                    note_duration = note.getElementsByTagName('duration')[0].childNodes[0].data
                    step = note.getElementsByTagName('step')[0].childNodes[0].data
                    octave = note.getElementsByTagName('octave')[0].childNodes[0].data
                    voice = note.getElementsByTagName('voice')[0].childNodes[0].data
                    note_type = note.getElementsByTagName('type')[0].childNodes[0].data
                    dot = len(note.getElementsByTagName('dot')) > 0 #true of false
                    staff = note.getElementsByTagName('staff')[0].childNodes[0].data
                    slur = None
                    tied = None
                    stem = None
                    beam = None
                    is_played = True
                    chord = -1

                    accidental = None
                    if 'accidental' in note_xml_string:
                        accidental = note.getElementsByTagName('accidental')[0].childNodes[0].data
                    if len(note.getElementsByTagName('slur')) > 0:
                        tmp_slur = {"type": None, "number": None, "placement": None}
                        tmp_slur["number"] = note.getElementsByTagName('slur')[0].attributes['number'].value
                        tmp_slur["type"] = note.getElementsByTagName('slur')[0].attributes['type'].value
                        if 'placement' in note.getElementsByTagName('slur')[0].attributes:
                            tmp_slur["placement"] = note.getElementsByTagName('slur')[0].attributes['placement'].value
                        slur = tmp_slur
                      
                    #*** CHANGE SLUR TO TIED??? ***
                    if len(note.getElementsByTagName('tied')) > 0:
                        tmp_tied = {"type": None, "number": None, "placement": None}
                        tmp_tied["number"] = 1#note.getElementsByTagName('slur')[0].attributes['number'].value
                        tmp_tied["type"] = note.getElementsByTagName('tied')[0].attributes['type'].value
                        slur = tmp_tied
                        tied = tmp_tied
                        if tmp_tied["type"] == "stop":
                          is_played = False
                    if len(note.getElementsByTagName('stem')) > 0:
                        stem = note.getElementsByTagName('stem')[0].childNodes[0].data
                    if len(note.getElementsByTagName('beam')) > 0:
                        beam_status = note.getElementsByTagName('beam')[0].childNodes[0].data
                        beam_number = note.getElementsByTagName('beam')[0].attributes['number'].value
                        beam = {"status": beam_status, "number": beam_number}
                    if len(note.getElementsByTagName('chord')) > 0:
                      if measure_musicxml_notes[-1]["chord"] == -1:
                        chord += 1
                        measure_musicxml_notes[-1]["chord"] = chord
                      chord = chord_number


                    note_name = ""
                    if accidental is None:
                        note_name = letters_to_notes[step] + "_" + octave
                        if letters_to_notes[step] in modifiers: #if there is a flat or sharp on this note
                            tmp_note_name_index = notes.index(note_name)
                            note_name = notes[tmp_note_name_index+modifiers[letters_to_notes[step]]]
                    elif accidental == "natural":
                        note_name = letters_to_notes[step] + "_" + octave
                    elif accidental == "sharp":
                        if step in ["C", "D", "F", "G", "A"]:
                            note_name = letters_to_notes[step] + "#_" + octave
                        else:
                            tmp_note_name = letters_to_notes[step] + "_" + octave
                            tmp_note_name_index = notes.index(tmp_note_name)
                            note_name = notes[tmp_note_name_index+1]
                    elif accidental == "flat":
                        tmp_note_name = letters_to_notes[step] + "_" + octave
                        tmp_note_name_index = notes.index(tmp_note_name)
                        note_name = notes[tmp_note_name_index-1]
                    elif accidental == "double-sharp":
                        tmp_note_name = letters_to_notes[step] + "_" + octave
                        tmp_note_name_index = notes.index(tmp_note_name)
                        note_name = notes[tmp_note_name_index+2]
                

                    index_in_notes = notes.index(note_name)

                    tmp_duration = duration if chord == -1 else measure_musicxml_notes[-1]["timestamp"]

                    measure_musicxml_notes.append({"note": note_name, "measure": measure_number, "timestamp": tmp_duration,
                                                   "index_in_notes": index_in_notes, "voice": voice,
                                                   "accidental": accidental, "note_type": note_type,
                                                   "dot": dot, "staff": staff, "slur": slur, "tied": tied, "step": step,
                                                   "octave": octave, "note_duration": note_duration, "stem": stem,
                                                   "beam": beam, "is_played": is_played, "note_id": note_id,
                                                   "chord": chord})
                    duration += int(note_duration) if chord == -1 else 0
                    note_id += 1
                
                elif 'rest' in note_xml_string:
                    rest = parseString(note_xml_string)
                    rest_duration = rest.getElementsByTagName('duration')[0].childNodes[0].data
                    staff = rest.getElementsByTagName('staff')[0].childNodes[0].data
                    voice = rest.getElementsByTagName('voice')[0].childNodes[0].data
                    staff = rest.getElementsByTagName('staff')[0].childNodes[0].data
                    dot = len(rest.getElementsByTagName('dot')) > 0
                    step = None
                    octave = None

                    if len(rest.getElementsByTagName('type')) == 0:
                        rest_type = "whole"
                    else:
                        rest_type = rest.getElementsByTagName('type')[0].childNodes[0].data
                    if len(rest.getElementsByTagName('display-step')) > 0 and len(rest.getElementsByTagName('display-octave')) > 0:
                        step = rest.getElementsByTagName('display-step')[0].childNodes[0].data
                        octave = rest.getElementsByTagName('display-octave')[0].childNodes[0].data
                    else:
                        if staff == "2":
                            step = "F"
                            octave = "3"
                        else:
                            step = "G"
                            octave = "4"

                    measure_musicxml_notes.append({"note": 'rest', "measure": measure_number, "timestamp": duration,
                                                   "index_in_notes": -1, "voice": voice,
                                                   "accidental": None, "note_type": rest_type,
                                                   "dot": dot, "staff": staff, "slur": None, "tied": None, "step": step,
                                                   "octave": octave, "note_duration": rest_duration, "stem": None,
                                                   "beam": None, "is_played": False, "note_id": note_id, "chord": -1})

                    duration += int(rest_duration)
                    note_id += 1

            elif child_of_measure.tag == "forward" or child_of_measure.tag == "backup":
                note_xml_string = ET.tostring(child_of_measure, encoding='unicode')
                movement = parseString(note_xml_string)
                sign = 1 if child_of_measure.tag == "forward" else -1
                movement_duration = movement.getElementsByTagName('duration')[0].childNodes[0].data
                duration += sign * int(movement_duration)
                #print(child_of_measure.tag, ": ", measure_number, " -- ", movement_duration, " - ", movement.toxml())

        musicxml_measures.append(measure_musicxml_notes)



from matplotlib.cbook import index_of
#TRANSFROM ARRAY OF MEASURES INTO FORMAT FOR VEXFLOW
def accidental_name_to_vexflow_notation(accidental):
    if accidental is None:
        return None
    else:
        accidental_translation = {"natural": "n", "sharp": "#", "flat": "b", "double-sharp": "##"}
        return accidental_translation[accidental]
def note_name_to_vexflow_notation(note, octave):
    if note is None:
        return 'b/4'
    else:
        note = note.lower()
        return note + "/" + octave
def note_duration_to_vexflow_notation(note_type, note, dotted):

    duration_translation = {"32nd": "32", "16th": "16", "eighth": "8",
                            "quarter": "q", "half": "h", "whole": "w",
                            "breve": "w"}
    duration = duration_translation[note_type]
    if dotted:
        duration = duration + "d"
    if note is "rest":
        return duration + "r"
    else:
        return duration

def get_buckets_stem(buckets):
    stem_translation = {"up": 1, "down": -1}
    stem = None
    for bucket in buckets:
        if bucket["stem"] is not None:
            if bucket["stem"] in stem_translation:
                stem = stem_translation[bucket["stem"]]
                break
            else:
                print(bucket["stem"])
    return stem

def get_buckets_beam(buckets):
    beam = None
    for bucket in buckets:
        if bucket["beam"] is not None:
            beam = bucket["beam"]
    return beam

def get_buckets_is_played(buckets):
    #true if at least one note is played in the note bucket
    is_played = False
    for bucket in buckets:
        if bucket["is_played"] is True:
            is_played = True
    return is_played

def get_song_array_index(buckets):
  song_array_index = -1
  for bucket in buckets:
    if bucket['song_array_index'] != -1:
      song_array_index = bucket['song_array_index']
      break
  return song_array_index

def find_buckets_with_match(start_stop, timestamp, slur_tie, number, list_to_match):
    matches = []
    if start_stop == "start":
        # type = slur/tie; timestamp of end > timestamp of start; slur_number = bucket slur_number; slur type = stop
        matches = [idx for idx, x in enumerate(list_to_match) if x["type"] == slur_tie and "end_timestamp" in x and int(x["end_timestamp"]) > int(timestamp) and int(x["number"]) == int(number)]
    elif start_stop == "stop":
        matches = [idx for idx, x in enumerate(list_to_match) if x["type"] == slur_tie and "start_timestamp" in x and int(x["start_timestamp"]) < int(timestamp) and int(x["number"]) == int(number)]
    return matches

def get_slurs(buckets, bucket_number, ties_and_slur):

    for index, bucket in enumerate(buckets):

        if bucket["slur"] is not None:
            slur = bucket["slur"]
            matches = find_buckets_with_match(slur["type"], bucket["timestamp"], "slur", slur["number"], ties_and_slur)
            if len(matches) == 0:
                if slur["type"] == "start":
                    ties_and_slur.append({"type": "slur", "number": slur["number"], "start_timestamp": bucket["timestamp"], "start_bucket_number": bucket_number, "start_note_rank": index, "start_voice": bucket["voice"], "start_placement": slur["placement"]})
                else:
                    ties_and_slur.append({"type": "slur", "number": slur["number"], "end_timestamp": bucket["timestamp"], "end_bucket_number": bucket_number, "end_note_rank": index, "end_voice": bucket["voice"], "end_placement": slur["placement"]})
            elif len(matches) == 1:
                match = ties_and_slur[matches[0]]
                match["type"] = "done"
                if slur["type"] == "start":
                    match["start_bucket_number"] = bucket_number
                    match["start_note_rank"] = index
                    match["start_voice"] =  bucket["voice"]
                    match["start_placement"] = slur["placement"]
                else:
                    match["end_bucket_number"] = bucket_number
                    match["end_note_rank"] = index
                    match["end_voice"] =  bucket["voice"]
                    match["end_placement"] = slur["placement"]
            else:
                print("more than one match!!!")

        if bucket["tied"] is not None:
            slur = bucket["tied"]
            matches = find_buckets_with_match(slur["type"], bucket["timestamp"], "tie", slur["number"], ties_and_slur)
            if len(matches) == 0:
                if slur["type"] == "start":
                    ties_and_slur.append({"type": "tie", "number": slur["number"], "start_timestamp": bucket["timestamp"], "start_bucket_number": bucket_number, "start_note_rank": index, "start_voice": bucket["voice"], "start_placement": slur["placement"]})
                else:
                    ties_and_slur.append({"type": "tie", "number": slur["number"], "end_timestamp": bucket["timestamp"], "end_bucket_number": bucket_number, "end_note_rank": index, "end_voice": bucket["voice"], "end_placement": slur["placement"]})
            elif len(matches) == 1:
                match = ties_and_slur[matches[0]]
                match["type"] = "done"
                if slur["type"] == "start":
                    match["start_bucket_number"] = bucket_number
                    match["start_note_rank"] = index
                    match["start_voice"] = bucket["voice"]
                    match["start_placement"] = slur["placement"]
                else:
                    match["end_bucket_number"] = bucket_number
                    match["end_note_rank"] = index
                    match["end_voice"] = bucket["voice"]
                    match["end_placement"] = slur["placement"]
            else:
                print("more than one match!!!")

    return ties_and_slur



musicxml_measures_by_voice = []
slurs_and_ties_by_measure = []

for measure in musicxml_measures:

    voices = {}
    #add voice number (key) with notes array (value) in voices
    for note in measure:
        voice = note["voice"]
        if voice not in voices:
            voices[voice] = [note]
        else:
            voices[voice].append(note)
  

    stave_notes_per_voice = {} #{"1": "stave_notes", "2": ...}
    slurs_and_ties = []

    for voice_number, voice_items in voices.items():
        #1. create buckets with all notes completely seperated {"1": [[bucket 1], [bucket 2], ...], "2": ...}
        voice_buckets_dict = {}
        for note in voice_items:
            if note["timestamp"] not in voice_buckets_dict:
                voice_buckets_dict[note["timestamp"]] = [note]
            else:
                voice_buckets_dict[note["timestamp"]].append(note)

        stave_notes = []
        buckets_number = 0
        for timestamp, buckets in voice_buckets_dict.items():

            #2. order notes in buckets by frequencies
            buckets = sorted(buckets, key=lambda d: d['index_in_notes'])

            slurs_and_ties = get_slurs(buckets, buckets_number, slurs_and_ties)

            buckets_number += 1

            tmp_buckets = []

            #3. merge them and create stave
            dot = buckets[0]["dot"]
            staff = buckets[0]["staff"]
            duration = note_duration_to_vexflow_notation(buckets[0]["note_type"], buckets[0]["note"], dot)
            stem = get_buckets_stem(buckets)
            beam = get_buckets_beam(buckets)
            song_array_index = get_song_array_index(buckets) #change this to a function to adapt for individual note analysis within a bucket (analys notes intensity of note individually even if played toghether)
            
            is_played = get_buckets_is_played(buckets)
            accidentals = []
            vexflow_notes = []
            for index, note in enumerate(buckets):
                accidental = accidental_name_to_vexflow_notation(note["accidental"])
                if accidental is not None:
                    accidentals.append({"accidental": accidental, "index": index})
            for index, note in enumerate(buckets):
                note = note_name_to_vexflow_notation(note["step"], note["octave"])
                vexflow_notes.append(note)

            stave_note = {"dotted": dot, "duration": duration, "accidentals": accidentals, "notes": vexflow_notes,
                          "staff": staff, "ghost": False, "stem": stem, "beam": beam,
                          "timestamp": timestamp, "note_type": buckets[0]["note_type"], "is_played": is_played,
                          "song_array_index": song_array_index}
            stave_notes.append(stave_note)

        stave_notes_per_voice[voice_number] = stave_notes
      
      #sort by timestamps?
    slurs_and_ties_by_measure.append(slurs_and_ties)

    musicxml_measures_by_voice.append(stave_notes_per_voice)


#Create new voices if timestamps are fcked up
#Create beams
#to add: 1.Beam directions 3.Position of rests

duration_translation = {"32nd": 0.125, "16th": 0.25, "eighth": 0.5,
                        "quarter": 1, "half": 2, "whole": 4,
                        "breve": 4}
def duration_estimation(note_type, dotted, divisions):

    if bucket["note_type"] in duration_translation:
        estimated_note_duration = divisions * duration_translation[note_type]
        if dotted:
          estimated_note_duration *= 1.5

        return estimated_note_duration
    else:
        print("note type not in duration_translation dictionnary")

def create_ghost_notes_array(timestamp, divisions, staff, measure_number):
    ghost_notes = []
    print("ghost: ", timestamp, " - ", divisions)
    while timestamp > 0:
        ghost_template = {"notes": ['c/4'], "accidentals": [], "dotted": False, "ghost": True, "staff": staff, "beam": None}
        if timestamp >= 4*divisions:
            ghost_template['duration'] = 'w'
            ghost_notes.append(ghost_template)
            timestamp -= 4*divisions
        elif timestamp >= 2*divisions:
            ghost_template['duration'] = 'h'
            ghost_notes.append(ghost_template)
            timestamp -= 2*divisions
        elif timestamp >= divisions:
            ghost_template['duration'] = 'q'
            ghost_notes.append(ghost_template)
            timestamp -= divisions
        elif timestamp >= 0.5*divisions:
            ghost_template['duration'] = '8'
            ghost_notes.append(ghost_template)
            timestamp -= 0.5*divisions
        elif timestamp >= 0.25*divisions:
            ghost_template['duration'] = '16'
            ghost_notes.append(ghost_template)
            timestamp -= 0.25*divisions
        elif timestamp >= 0.125*divisions:
            ghost_template['duration'] = '32'
            ghost_notes.append(ghost_template)
            timestamp -= 0.125*divisions
        else:
            return None

    return ghost_notes

def is_not_only_ghosts(buckets):
    is_not_just_ghosts = False
    for bucket in buckets:
        if bucket["ghost"] == False:
            return True
    return False

time_by_measure = divisions*4/time_signature_denominator*time_signature_numerator
tmp_musicxml_measures_by_voice = []
for measure_index, measure in enumerate(musicxml_measures_by_voice):
    tmp_measure = {}

    for voice_number, voice_items in measure.items():
        if True:
            estimated_timestamp = 0

            new_voices = {}
            last_voice_number = voice_number
            last_voice_notes = []

            staff = voice_items[0]["staff"]

            for index, bucket in enumerate(voice_items):

                if estimated_timestamp != bucket["timestamp"]:
                    previous_bucket = voice_items[index - 1]
                    time_of_ghost_notes_to_fill = time_by_measure - previous_bucket["timestamp"] - duration_estimation(previous_bucket["note_type"], previous_bucket["dotted"], divisions)
                    #print("one: ", time_of_ghost_notes_to_fill)
                    ghost_notes_array = create_ghost_notes_array(time_of_ghost_notes_to_fill, divisions, staff, measure_index)
                    last_voice_notes += ghost_notes_array
                    if len(last_voice_notes) > 0 and is_not_only_ghosts(last_voice_notes):
                        new_voices[last_voice_number] = last_voice_notes
                    last_voice_number = str(int(last_voice_number)*10)
                    
                    last_voice_notes = create_ghost_notes_array(bucket["timestamp"], divisions, staff, measure_index)
                    #print("two: ", bucket["timestamp"])
                    last_voice_notes.append(bucket)

                    estimated_timestamp = bucket["timestamp"] + duration_estimation(bucket["note_type"], bucket["dotted"], divisions)
                else:
                    last_voice_notes.append(bucket)
                    estimated_timestamp += duration_estimation(bucket["note_type"], bucket["dotted"], divisions)

                print(voice_number, " - ", estimated_timestamp)
                if index+1 == len(voice_items):
                    #time_of_ghost_notes_to_fill = time_by_measure - bucket["timestamp"] + duration_estimation(bucket["note_type"], bucket["dotted"], divisions)
                    time_of_ghost_notes_to_fill = time_by_measure - estimated_timestamp
                    #print("three: ", time_of_ghost_notes_to_fill)
                    last_voice_notes += create_ghost_notes_array(time_of_ghost_notes_to_fill, divisions, staff, measure_index)
                    if len(last_voice_notes) > 0 and is_not_only_ghosts(last_voice_notes):
                        new_voices[last_voice_number] = last_voice_notes


            for sub_voice_number, sub_voice_items in new_voices.items():
                tmp_measure[sub_voice_number] = sub_voice_items

    tmp_musicxml_measures_by_voice.append(tmp_measure)

for measure_number, measure in enumerate(tmp_musicxml_measures_by_voice):
    for voice_number in list(measure):
        voice_items = measure[voice_number]
        beams_voice = []
        for index, vexflow_note in enumerate(voice_items):
            if vexflow_note['beam'] is not None:
                if vexflow_note['beam']['status'] == 'begin':
                    beams_voice.append({"begin": index})
                elif vexflow_note['beam']['status'] == 'end':
                    if 'begin' in beams_voice[-1]:
                        beams_voice[-1]["end"] = index+1
                    else:
                        print("beam is not terminated")
        print(len(beams_voice))
        if len(beams_voice) > 0:
            beam_voice_key = voice_number + "_beams"
            tmp_musicxml_measures_by_voice[measure_number][beam_voice_key] = beams_voice

for measure_number, measure in enumerate(tmp_musicxml_measures_by_voice):
    measure["slurs_and_ties"] = slurs_and_ties_by_measure[measure_number]
    measure["layout"] = layouts[measure_number]


#SAVE THE VEXFLOW ARRAY
import json
data = {"measures": tmp_musicxml_measures_by_voice}
with open('vexflow_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
