> ## Documentation Index
> Fetch the complete documentation index at: https://docs.vast.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Volumes

The [**Storage**](https://cloud.vast.ai/storage/) page allows you to easily access and manage your **volumes -** storage that can be attached to your instances for data storage.

We currently provide **local volumes only**, meaning:

* A volume is physically tied to the machine it was created on.
* It can only be attached to instances running on the same physical machine.
* It cannot be moved or attached to instances on other machines.

<Note>
  Volume size cannot be changed after creation, so be sure to choose the size carefully based on your expected storage needs.&#x20;
</Note>

## Creating a Volume in GUI

This guide will walk you through the process of creating a volume using a template in the GUI. You can create the volume during instance creation by using a template with volume settings enabled, or you can create a volume by using dropdown menu on the Search page.&#x20;

### **How to create a volume via Add volume dropdown menu on the Search page?**

1. Select a template then click on **Add volume** dropdown. You will see an option labeled **Local volume** with a + (plus) button next to it.

   <img src="https://mintcdn.com/vastai-80aa3a82/1a9mKbP8zn3lYY0d/images/volumes.webp?fit=max&auto=format&n=1a9mKbP8zn3lYY0d&q=85&s=d818347fcfa8ee7b670e80b32ac995fe" alt="" width="1280" height="674" data-path="images/volumes.webp" />
2. Click + button. This will allow you to adjust the volume size using the slider. Once enabled, offes will display the available volume size.&#x20;

   <Frame caption="Create local volume">
     <img src="https://mintcdn.com/vastai-80aa3a82/1a9mKbP8zn3lYY0d/images/volumes-2.webp?fit=max&auto=format&n=1a9mKbP8zn3lYY0d&q=85&s=9bb72e7030922749446069dc9b84eab6" alt="Create local volume" width="1280" height="712" data-path="images/volumes-2.webp" />
   </Frame>
3. Click **Rent **button to launch your instance along with the volume. Once the instance is running, your volume will be automatically mounted and available inside the container at the /data directory.

   <Frame caption="Volume on instance">
     <img src="https://mintcdn.com/vastai-80aa3a82/1a9mKbP8zn3lYY0d/images/volumes-3.webp?fit=max&auto=format&n=1a9mKbP8zn3lYY0d&q=85&s=7b38d96b6f8e241b5415e530556ccad2" alt="Volume on instance" width="1018" height="645" data-path="images/volumes-3.webp" />
   </Frame>
4. You can find your volume information on **Storage **page.

   <Frame caption="Volume info">
     <img src="https://mintcdn.com/vastai-80aa3a82/1a9mKbP8zn3lYY0d/images/volumes-4.webp?fit=max&auto=format&n=1a9mKbP8zn3lYY0d&q=85&s=701c608adba8e5806f535276ed7a31d6" alt="Volume info" width="1280" height="525" data-path="images/volumes-4.webp" />
   </Frame>

### **How to create a volume using a template?**

1. Choose  a Template. You can either choose an existing template from the [**Recommended**](https://cloud.vast.ai/templates/) list or create your own [custom template](/guides/templates/creating-templates).
2. Open Template Editor (Click on pencil icon on a template card). Scroll down until you see the **Disk Space (Container + Volume) **section.&#x20;

   <img src="https://mintcdn.com/vastai-80aa3a82/1a9mKbP8zn3lYY0d/images/volumes-5.webp?fit=max&auto=format&n=1a9mKbP8zn3lYY0d&q=85&s=a05044602cb747bb9cc9713e13c523e1" alt="Volume settings" width="800" height="657" data-path="images/volumes-5.webp" />
3. In this section, check the box **Add recommended volume settings**. Once selected, a new configuration area will appear where you can enter the **volume size **and specify the **installation path. **A default path is provided, but you can modify it if needed.&#x20;

   <Frame caption="Volume settings">
     <img src="https://mintcdn.com/vastai-80aa3a82/1a9mKbP8zn3lYY0d/images/volumes-6.webp?fit=max&auto=format&n=1a9mKbP8zn3lYY0d&q=85&s=d107bd4b36b023ddf52444b5bdcb5edd" alt="Volume settings" width="1049" height="354" data-path="images/volumes-6.webp" />
   </Frame>
4. After filling in the volume details, click **Save\&Use **or **Create\&Use Template **to apply your changes and navigate to the Search page. Offers that support volumes will now display a volume badge showing the available volume size. You can adjust the volume size using the slider in the Search page after your template is configured.

   <img src="https://mintcdn.com/vastai-80aa3a82/1a9mKbP8zn3lYY0d/images/volumes-7.webp?fit=max&auto=format&n=1a9mKbP8zn3lYY0d&q=85&s=c70715c2f8c2ad95a6b154ddcaaa286a" alt="Volume settings" width="1280" height="676" data-path="images/volumes-7.webp" />
5. Select a GPU and click **Rent **button.

### **How to view volume pricing?**

To view pricing details, simply hover over the Rent button for any offer.&#x20;

<img src="https://mintcdn.com/vastai-80aa3a82/1a9mKbP8zn3lYY0d/images/volumes-8.webp?fit=max&auto=format&n=1a9mKbP8zn3lYY0d&q=85&s=f0d07bb5a6cd540184f7e2498eb287ac" alt="" width="800" height="375" data-path="images/volumes-8.webp" />

### Deleting volume

To delete a volume, the instance it is attached to must be **deleted first**. Deleting a volume that is currently **mounted to a running or stopped instance is not allowed**.

Delete a Volume:

1. Make sure the volume is **not attached** to any instance.
   &#x20;If it is, **delete the instance** first from the Instances page.
2. Once the volume is detached, go to the **Storage** page.
3. Find the volume you want to delete, click on the **three-dot menu** (⋮) next to it, and select **"Delete volume"**.

   <Frame caption="Delete volume">
     <img src="https://mintcdn.com/vastai-80aa3a82/1a9mKbP8zn3lYY0d/images/volumes-9.webp?fit=max&auto=format&n=1a9mKbP8zn3lYY0d&q=85&s=cb0d822b0931c74b3f25b9ddddd960e4" alt="Delete volume" width="1280" height="540" data-path="images/volumes-9.webp" />
   </Frame>
4. Confirm the deletion. This action is **permanent** and cannot be undone.

<Warning>
  Important: Deleting a volume will permanently remove all data stored in it. Make sure to back up any important data before proceeding.
</Warning>

### How to create an instance with existing volume?

If you already have a volume and want to launch a new instance using it, follow these steps:

1. Go to the **Storage** page and select the volume you want to use.

2. In the **Volume Info** section, you will see a button labeled **Rent instance using this volume**.

   <img src="https://mintcdn.com/vastai-80aa3a82/1a9mKbP8zn3lYY0d/images/volumes-10.webp?fit=max&auto=format&n=1a9mKbP8zn3lYY0d&q=85&s=8c4db1caeb318e91efe1850d0fdcacfc" alt="Rent instance using this volume" width="1280" height="884" data-path="images/volumes-10.webp" />

3. Click this button. You will be redirected to the **Search Page**, where available offers are automatically filtered to match the **same machine** where the volume is located.

4. Select your preferred offer and proceed to launch the instance.
   &#x20;The selected volume will be automatically attached to the instance upon creation.

## Creating a Volume in CLI

To create a volume, you can use the vast CLI. See our [CLI documentation](https://cloud.vast.ai/cli/) for set-up and usage of the CLI. You can search for volume offers using the command:

```text Text theme={null}
vastai search volumes
```

There is a modified list of search params available, for more information, you can add the -- help option to the search.&#x20;

This will bring up a list of available volume offers. You will be able to see the maximum capacity for the volume (in Gigabytes). Just like creating an instance, you can copy the offer ID and create a volume with the command:

```text Text theme={null}
  vastai create volume <offer_id> -s <volume_size> -n <name>
```

This will send a command to the host machine to allocate the given space to your volume. You can optionally specify a name with -n, it can be alphanumeric with underscores, with a max length of 64. If all goes well, you should be able to see your volume as created when you run the command&#x20;

```text Text theme={null}
vastai show volumes
```

### How can I  create an instance with a volume?

Now that your volume is created, you can use it by creating an instance on the machine with the volume, and passing the volume in the env argument. The format is -v \<volume\_name>:\<mount\_point>, for example:&#x20;

```text Text theme={null}
vastai create instance 874 --image pytorch/pytorch --env '-v V.881:/mnt' --disk 30 --ssh --direct
```

That command mounts your volume at the directory /mnt. The directory does not need to exist in order to be mounted.

### Can I use my volume on a different machine?

No. Volumes are local, they are physically tied to the machine they were created on and cannot be moved or attached to instances on other machines.

However, you can **copy data** between volumes on different machines using the `vastai copy` command with the `V.volume_id:path` format:

```text Text theme={null}
vastai copy V.<src_volume_id>:/data/ V.<dst_volume_id>:/data/
```

You can also copy between a volume and a running instance:

```text Text theme={null}
vastai copy V.<volume_id>:/data/ C.<instance_id>:/workspace/
vastai copy C.<instance_id>:/workspace/ V.<volume_id>:/data/
```

Volumes also work with [Cloud Copy](/guides/instances/storage/cloud-sync), so you can copy between a volume and a connected cloud storage provider (S3, Google Drive, etc.):

```text Text theme={null}
vastai copy s3.<connection_id>:/data/ V.<volume_id>:/data/
vastai copy V.<volume_id>:/data/ s3.<connection_id>:/data/
```

Note: Copying directly between a volume and your local machine is not supported.

### How can I delete my volume?

When you're done using it, you can delete your volume using the command&#x20;

```text Text theme={null}
vastai delete volume <volume_id>
```

<Warning>
  This will only work if all instances using the volume have been destroyed.&#x20;
</Warning>

### How can I see what instances are using my volume?

The command

```text Text theme={null}
vastai show volumes
```

will display a list of volumes you own, as well as what instances exist that are using that volume.

## A machine with my volume went offline! Am I still being charged?

Just like with normal instances, you are never charged when a machine is offline. This is usually a temporary issue, and when the machine comes back online, volume charges will resume as normal. If you wish to delete the volume in the meantime, you can do so, and you will not be charged when the machine comes back online. If the machine is offline for an extended period of time, please reach out to vast support.&#x20;

## Can I use my volume with a VM instance?

At this time, volumes are only supported for docker instances, and cannot be used with VM instances.
