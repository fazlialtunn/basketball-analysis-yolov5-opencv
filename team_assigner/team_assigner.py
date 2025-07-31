from PIL import Image
import cv2
from transformers import CLIPProcessor, CLIPModel
import sys
sys.path.append("../")
from utils import read_stub, save_stub

class TeamAssigner:
    def __init__(self, team_1_class_name = "white shirt", team_2_class_name = "dark red shirt"):
        self.team_1_class_name = team_1_class_name
        self.team_2_class_name = team_2_class_name
        self.team_player_dict = {}
        
    def load_model(self):
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    def get_player_color(self, frame, bbox):
        image = frame[int(bbox[1]):int(bbox[3]), int(bbox[0]):int(bbox[2])]
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)

        classes = [self.team_1_class_name, self.team_2_class_name]

        inputs = self.processor(text=classes, images=pil_image, return_tensors="pt", padding=True)
        outputs = self.model(**inputs)
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1)
        return classes[probs.argmax(dim = 1)[0]] 

    def get_player_team(self, frame, player_bbox, player_id):

        if player_id in self.team_player_dict:
            return self.team_player_dict[player_id]

        player_color = self.get_player_color(frame, player_bbox)
        team_id = 2
        if player_color == self.team_1_class_name:
            team_id = 1
        self.team_player_dict[player_id] = team_id    
        return team_id
    
    def get_player_teams_across_frames(self, video_frames,player_tracks, read_from_stub = False, stub_path = None):
        player_assignments = read_stub(stub_path, read_from_stub)
        if player_assignments is not None:
            if len(player_assignments) == len(video_frames):
                return player_assignments
            
        self.load_model()
        player_assignments = []

        for frame_num, player_track in enumerate(player_tracks):
            player_assignments.append({})

            if frame_num % 50 == 0:
                self.team_player_dict = {}

            for player_id, track in player_track.items():
                team = self.get_player_team(video_frames[frame_num], track["bbox"], player_id)
                player_assignments[frame_num][player_id] = team
        save_stub(stub_path, player_assignments)       
        return player_assignments
