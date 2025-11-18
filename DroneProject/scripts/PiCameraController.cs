using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;

[Serializable]
public class PiPreset
{
    public string label;
    public int width;
    public int height;
    public int fps;
}

public class PiCameraController : MonoBehaviour
{
    [Header("Pi Server")]
    public string baseUrl = "http://192.168.0.165:5000";

    [Header("Presets (edit in Inspector)")]
    public PiPreset[] presets = new PiPreset[]
    {
        new PiPreset{ label = "640×480 @15",   width = 640,  height = 480,  fps = 15 },
        new PiPreset{ label = "1280×720 @30",  width = 1280, height = 720,  fps = 30 },
        new PiPreset{ label = "1920×1080 @30", width = 1920, height = 1080, fps = 30 },
    };

    [Header("UI")]
    public Text statusLabel;        // Assign a Text (Legacy) UI element
    public Text nextButtonText;     // (Optional) assign your button's Text to show "Next: ..."

    int index = 0;
    bool busy = false;

    void Start()
    {
        // Show initial "Active" state on play
        if (presets != null && presets.Length > 0)
        {
            // Apply current preset to Pi so UI reflects reality
            ApplyCurrentPreset();
            UpdateNextButtonLabel();
        }
        else
        {
            UpdateStatus("No presets configured");
        }
    }

    public void NextPreset()
    {
        if (busy || presets == null || presets.Length == 0) return;
        index = (index + 1) % presets.Length;
        ApplyCurrentPreset();      // apply immediately
        UpdateNextButtonLabel();   // refresh "Next: ..." label
    }

    public void ApplyCurrentPreset()
    {
        if (busy || presets == null || presets.Length == 0) return;
        var p = presets[index];
        StartCoroutine(SetPresetRoutine(p));
    }

    IEnumerator SetPresetRoutine(PiPreset p)
    {
        busy = true;
        UpdateStatus($"Setting {p.label} ...");

        string url = $"{baseUrl}/set?w={p.width}&h={p.height}&fps={p.fps}";
        using (var req = UnityWebRequest.Get(url))
        {
            req.timeout = 5; // seconds
            yield return req.SendWebRequest();

#if UNITY_2020_2_OR_NEWER
            bool ok = (req.result == UnityWebRequest.Result.Success);
#else
            bool ok = !(req.isNetworkError || req.isHttpError);
#endif
            if (!ok)
            {
                UpdateStatus($"Failed: {req.error}");
            }
            else
            {
                // Success: show the active preset
                UpdateStatus($"Active: {p.label}");
            }
        }

        busy = false;
    }

    void UpdateStatus(string msg)
    {
        if (statusLabel != null) statusLabel.text = msg;
        Debug.Log($"PiCameraController: {msg}");
    }

    void UpdateNextButtonLabel()
    {
        if (nextButtonText == null || presets == null || presets.Length == 0) return;

        // Next index wraps around
        int next = (index + 1) % presets.Length;
        var np = presets[next];
        nextButtonText.text = $"Next: {np.label}";
    }
}